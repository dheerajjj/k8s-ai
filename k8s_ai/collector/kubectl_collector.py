from __future__ import annotations

import json
import logging
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)


class KubectlError(RuntimeError):
    pass


class KubectlCollector:
    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds

    def list_pod_containers(self, namespace: str, pod: str) -> List[str]:
        cmd = [
            "kubectl",
            "get",
            "pod",
            pod,
            "-n",
            namespace,
            "-o",
            "json",
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise KubectlError(f"Timed out while listing containers for pod '{pod}'.") from exc

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            raise KubectlError(f"kubectl get pod failed: {stderr or 'unknown error'}")

        try:
            data = json.loads(proc.stdout)
            containers = data["spec"]["containers"]
            return [c["name"] for c in containers if "name" in c]
        except Exception as exc:  # noqa: BLE001
            raise KubectlError("Failed to parse pod container list from kubectl JSON output.") from exc

    def get_logs(
        self,
        namespace: str,
        pod: str,
        container: Optional[str] = None,
        previous: bool = False,
        tail_lines: int = 3000,
    ) -> str:
        cmd = ["kubectl", "logs", pod, "-n", namespace, f"--tail={tail_lines}"]
        if container:
            cmd.extend(["-c", container])
        if previous:
            cmd.append("--previous")

        logger.debug("Running command: %s", " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            which = f"container '{container}' " if container else ""
            raise KubectlError(f"Timed out while fetching logs for {which}pod '{pod}'.") from exc

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            msg = stderr or "unknown kubectl logs error"
            raise KubectlError(f"kubectl logs failed: {msg}")

        return proc.stdout or ""
