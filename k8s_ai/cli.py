from __future__ import annotations

import logging
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from k8s_ai.analyzer import LLMAnalyzer
from k8s_ai.collector import KubectlCollector
from k8s_ai.config import Settings
from k8s_ai.fixer import augment_with_safe_kubectl_commands
from k8s_ai.logging_setup import setup_logging
from k8s_ai.models import ContainerLog, PodAnalysisReport
from k8s_ai.utils import redact_sensitive_content, smart_truncate

app = typer.Typer(help="Kubernetes Log Analyzer Agent")
console = Console()
logger = logging.getLogger(__name__)


def _collect_logs_for_containers(
    collector: KubectlCollector,
    settings: Settings,
    namespace: str,
    pod: str,
    container: Optional[str],
    previous: bool,
    mock: bool,
) -> List[ContainerLog]:
    if mock:
        mock_container = container or "app"
        raw_log = """2026-02-17T10:00:00Z INFO starting service name=orders-api
2026-02-17T10:00:02Z ERROR db connection timeout host=postgres.default.svc.cluster.local:5432
2026-02-17T10:00:03Z WARN retrying database connection attempt=1/5
2026-02-17T10:00:04Z ERROR permission denied path=/var/lib/app/cache
2026-02-17T10:00:05Z ERROR upstream request failed status=500 route=/api/v1/orders latency_ms=8123
2026-02-17T10:00:06Z ERROR JavaScript heap out of memory
2026-02-17T10:00:07Z WARN kubelet reported Last State: Terminated reason=OOMKilled
2026-02-17T10:00:08Z WARN back-off restarting failed container reason=CrashLoopBackOff
"""
        redacted = redact_sensitive_content(raw_log)
        truncated, is_truncated = smart_truncate(redacted, settings.max_log_chars)
        return [
            ContainerLog(
                container=mock_container,
                raw_log=raw_log,
                redacted_log=redacted,
                truncated_log=truncated,
                is_truncated=is_truncated,
            )
        ]
    if container:
        containers = [container]
    else:
        containers = collector.list_pod_containers(namespace=namespace, pod=pod)
        if not containers:
            raise typer.BadParameter("No containers found in the pod.")

    results: List[ContainerLog] = []
    for c in containers:
        raw_log = collector.get_logs(
            namespace=namespace,
            pod=pod,
            container=c,
            previous=previous,
        )
        redacted = redact_sensitive_content(raw_log)
        truncated, is_truncated = smart_truncate(redacted, settings.max_log_chars)
        results.append(
            ContainerLog(
                container=c,
                raw_log=raw_log,
                redacted_log=redacted,
                truncated_log=truncated,
                is_truncated=is_truncated,
            )
        )
    return results


def _print_report(report: PodAnalysisReport) -> None:
    header = (
        f"[bold cyan]Analysis complete[/bold cyan]\n"
        f"Namespace: [green]{report.namespace}[/green]\n"
        f"Pod: [green]{report.pod}[/green]\n"
        f"Using previous logs: [yellow]{report.used_previous_logs}[/yellow]"
    )
    console.print(Panel.fit(header))

    for container, result in report.container_reports:
        table = Table(title=f"Container: {container}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_row("Root cause", result.root_cause)
        table.add_row("Confidence", f"{result.confidence:.2f}")
        table.add_row("Detected issues", ", ".join(result.detected_issues) or "none")
        table.add_row("Fix steps", "\n".join(f"- {s}" for s in result.remediation_steps) or "- none")
        table.add_row(
            "Suggested kubectl commands",
            "\n".join(f"- {c}" for c in result.suggested_kubectl_commands) or "- none",
        )
        if result.notes:
            table.add_row("Notes", result.notes)
        console.print(table)


@app.command("analyze")
def analyze_command(
    namespace: str = typer.Argument(..., help="Kubernetes namespace"),
    pod: str = typer.Argument(..., help="Pod name"),
    container: Optional[str] = typer.Option(None, "--container", "-c", help="Container name"),
    previous: bool = typer.Option(False, "--previous", help="Use previous container logs"),
    timeout: Optional[int] = typer.Option(None, "--timeout", help="kubectl command timeout in seconds"),
    mock: bool = typer.Option(False, "--mock", help="Enable offline mock analysis mode"),
) -> None:
    settings = Settings.from_env()
    setup_logging(settings.log_level)
    run_timeout = timeout if timeout is not None else settings.timeout_seconds
    use_mock = mock or settings.mock_mode

    try:
        collector = KubectlCollector(timeout_seconds=run_timeout)
        analyzer = LLMAnalyzer(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            mock_mode=use_mock,
        )

        if not use_mock and not settings.llm_api_key:
            raise typer.BadParameter("LLM_API_KEY is required unless --mock mode is used.")

        logs = _collect_logs_for_containers(
            collector=collector,
            settings=settings,
            namespace=namespace,
            pod=pod,
            container=container,
            previous=previous,
            mock=use_mock,
        )

        report = PodAnalysisReport(namespace=namespace, pod=pod, used_previous_logs=previous)

        for entry in logs:
            result = analyzer.analyze(
                namespace=namespace,
                pod=pod,
                container=entry.container,
                log_text=entry.truncated_log,
            )
            result = augment_with_safe_kubectl_commands(result, namespace, pod, entry.container)
            report.container_reports.append((entry.container, result))

        _print_report(report)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Analysis failed.")
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
