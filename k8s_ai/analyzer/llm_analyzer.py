from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from openai import OpenAI

from k8s_ai.models import AnalysisResult

logger = logging.getLogger(__name__)

ISSUE_CATALOG = [
    "CrashLoopBackOff",
    "OOMKilled",
    "ImagePullBackOff",
    "DBConnectionError",
    "Timeout",
    "PermissionIssue",
]


class LLMAnalyzer:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.0,
        mock_mode: bool = False,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.mock_mode = mock_mode
        self.client = None if mock_mode else OpenAI(api_key=api_key, base_url=base_url)

    def analyze(self, namespace: str, pod: str, container: str, log_text: str) -> AnalysisResult:
        if self.mock_mode:
            return self._mock_result(log_text)

        system_prompt = (
            "You are a senior Kubernetes SRE assistant. Analyze logs to find likely root cause. "
            "Never request secrets. Provide safe, non-destructive remediation and kubectl suggestions."
        )

        user_payload: Dict[str, Any] = {
            "namespace": namespace,
            "pod": pod,
            "container": container,
            "known_issue_types": ISSUE_CATALOG,
            "instructions": [
                "Return strict JSON only.",
                "confidence must be 0..1 float.",
                "detected_issues must use canonical identifiers: "
                "crashloopbackoff, oomkilled, imagepullbackoff, db_connection_error, timeout, permission_issue, other.",
                "Never include secrets in output.",
            ],
            "log_excerpt": log_text,
            "json_schema": {
                "root_cause": "string",
                "confidence": "float(0..1)",
                "detected_issues": ["string"],
                "remediation_steps": ["string"],
                "suggested_kubectl_commands": ["string"],
                "notes": "string optional",
            },
        }

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        logger.debug("LLM response raw JSON: %s", content)
        parsed = json.loads(content)
        return self._to_result(parsed)

    @staticmethod
    def _to_result(data: Dict[str, Any]) -> AnalysisResult:
        return AnalysisResult(
            root_cause=str(data.get("root_cause", "Unable to determine root cause.")),
            confidence=max(0.0, min(1.0, float(data.get("confidence", 0.35)))),
            detected_issues=[str(i) for i in data.get("detected_issues", ["other"])],
            remediation_steps=[str(i) for i in data.get("remediation_steps", [])],
            suggested_kubectl_commands=[str(i) for i in data.get("suggested_kubectl_commands", [])],
            notes=str(data.get("notes")) if data.get("notes") is not None else None,
        )

    @staticmethod
    def _mock_result(log_text: str) -> AnalysisResult:
        l = log_text.lower()
        issues: List[str] = []
        cause = "Application failure due to unknown runtime error."
        confidence = 0.55
        steps = [
            "Inspect pod events and container state details.",
            "Validate image, environment variables, and service dependencies.",
        ]
        cmds = []

        if "crashloopbackoff" in l:
            issues.append("crashloopbackoff")
            cause = "Container repeatedly crashes and restarts (CrashLoopBackOff)."
            confidence = 0.9
            steps.insert(0, "Check startup command and application exception stack trace.")
        if "oomkilled" in l or "out of memory" in l:
            issues.append("oomkilled")
            cause = "Container terminated due to memory limit breach (OOMKilled)."
            confidence = max(confidence, 0.92)
            steps.insert(0, "Increase memory limits/requests and investigate memory spikes.")
        if "imagepullbackoff" in l or "errimagepull" in l:
            issues.append("imagepullbackoff")
            cause = "Kubernetes cannot pull the container image."
            confidence = max(confidence, 0.9)
            steps.insert(0, "Verify image name/tag and imagePullSecrets.")
        if "connection refused" in l or "db" in l and "timeout" in l:
            issues.append("db_connection_error")
            cause = "Application cannot connect to its database dependency."
            confidence = max(confidence, 0.8)
            steps.insert(0, "Verify DB host/port, DNS, credentials, and network policy.")
        if "permission denied" in l or "forbidden" in l:
            issues.append("permission_issue")
            cause = "Permission or RBAC error is blocking workload behavior."
            confidence = max(confidence, 0.85)
            steps.insert(0, "Review service account permissions and filesystem access policy.")
        if not issues:
            issues = ["other"]

        return AnalysisResult(
            root_cause=cause,
            confidence=confidence,
            detected_issues=issues,
            remediation_steps=steps[:6],
            suggested_kubectl_commands=cmds,
            notes="Generated in offline mock mode.",
        )
