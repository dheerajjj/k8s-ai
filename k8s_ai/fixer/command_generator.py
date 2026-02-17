from __future__ import annotations

from typing import List

from k8s_ai.models import AnalysisResult


def augment_with_safe_kubectl_commands(
    result: AnalysisResult, namespace: str, pod: str, container: str
) -> AnalysisResult:
    commands: List[str] = list(result.suggested_kubectl_commands)
    issues = {i.lower() for i in result.detected_issues}

    def add(cmd: str) -> None:
        if cmd not in commands:
            commands.append(cmd)

    add(f"kubectl describe pod {pod} -n {namespace}")
    add(f"kubectl get events -n {namespace} --sort-by=.metadata.creationTimestamp")
    add(f"kubectl logs {pod} -n {namespace} -c {container} --previous --tail=200")

    if "crashloopbackoff" in issues:
        add(f"kubectl rollout restart deployment/<deployment-name> -n {namespace}")
    if "oomkilled" in issues:
        add(
            f"kubectl set resources deployment/<deployment-name> -n {namespace} "
            "--limits=memory=1Gi --requests=memory=512Mi"
        )
    if "imagepullbackoff" in issues:
        add(f"kubectl get secret -n {namespace}")
        add(f"kubectl describe pod {pod} -n {namespace} | findstr /I \"image\"")
    if "permission_issue" in issues:
        add(f"kubectl auth can-i get pods -n {namespace}")

    result.suggested_kubectl_commands = commands
    return result
