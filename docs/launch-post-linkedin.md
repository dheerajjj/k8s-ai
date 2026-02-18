I’ve published **k8s-ai** (PyPI package: `k8s-ai-cli`), a Python CLI focused on Kubernetes incident triage.

`k8s-ai` reads pod logs via `kubectl` and provides:
- likely root cause
- confidence level
- remediation guidance
- practical follow-up `kubectl` commands

It includes:
- `--mock` mode for local testing without a cluster
- `--previous` log analysis for CrashLoopBackOff scenarios
- container-level targeting for multi-container pods

Install:
```bash
pip install k8s-ai-cli
```

Run:
```bash
k8s-ai --help
k8s-ai analyze --mock
k8s-ai analyze --pod <pod> --namespace <namespace>
```

PyPI: https://pypi.org/project/k8s-ai-cli/
