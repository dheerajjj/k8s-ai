Launched **k8s-ai** (PyPI package: `k8s-ai-cli`) — a CLI for faster Kubernetes pod log triage.

It reads pod logs using your local `kubectl` context and returns:
- likely root cause
- confidence level
- suggested remediation steps
- useful follow-up `kubectl` commands

It also supports:
- `--mock` mode (no cluster required)
- `--previous` logs (helpful for CrashLoopBackOff)
- specific container selection for multi-container pods

Install:
```bash
pip install k8s-ai-cli
```

Examples:
```bash
k8s-ai analyze --mock
k8s-ai analyze --pod my-pod --namespace my-ns
k8s-ai analyze --pod my-pod --namespace my-ns --previous
k8s-ai analyze --pod my-pod --namespace my-ns --container app
```

Would appreciate feedback from DevOps/SRE folks on output quality and what additional signals would be most useful next.
