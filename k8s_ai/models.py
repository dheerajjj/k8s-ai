from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ContainerLog:
    container: str
    raw_log: str
    redacted_log: str
    truncated_log: str
    is_truncated: bool


@dataclass
class AnalysisResult:
    root_cause: str
    confidence: float
    detected_issues: List[str]
    remediation_steps: List[str]
    suggested_kubectl_commands: List[str]
    notes: Optional[str] = None


@dataclass
class PodAnalysisReport:
    namespace: str
    pod: str
    used_previous_logs: bool
    container_reports: List[tuple[str, AnalysisResult]] = field(default_factory=list)
