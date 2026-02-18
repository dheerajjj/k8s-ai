# k8s-ai

`k8s-ai` is a Python CLI for Kubernetes log triage. It reads pod logs via `kubectl` and provides:
- likely root cause
- confidence level
- suggested remediation steps
- helpful follow-up `kubectl` commands

Designed for DevOps engineers, SREs, platform teams, and Kubernetes developers.

## Install
```bash
pip install k8s-ai-cli
```

## Quick Start
```bash
# help
k8s-ai --help

# analyze a pod
k8s-ai analyze --pod my-pod-abc123 --namespace production
```

## Mock Example (No Cluster Required)
```bash
k8s-ai analyze --mock
```

## Real Cluster Examples
```bash
# current logs
k8s-ai analyze --pod checkout-7f9d8c6f95-2kq9m --namespace payments

# previous logs (useful for CrashLoopBackOff)
k8s-ai analyze --pod api-6b8f74d9f7-ptc2z --namespace backend --previous

# specific container in a multi-container pod
k8s-ai analyze --pod worker-5c7bbf6d8d-v8l2r --namespace jobs --container processor
```

## Safety
`k8s-ai` runs locally and uses your local `kubectl` context. It does not store logs by default.

## Features
- AI-assisted root-cause analysis from pod logs
- Confidence scoring for diagnosis quality
- Actionable remediation guidance
- Suggested `kubectl` follow-up commands
- `--mock` mode for offline testing
- `--previous` support for restarted containers
- `--container` selection for multi-container pods

## License
MIT

