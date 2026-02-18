# v0.1.1

`k8s-ai` is a CLI for Kubernetes incident triage. It reads pod logs via `kubectl` and returns probable root cause, confidence level, remediation guidance, and practical follow-up commands.

## Key Features
- Pod log analysis for faster first-pass debugging
- Confidence level for each diagnosis
- Suggested remediation steps
- Helpful `kubectl` commands for next actions
- `--mock` mode (no cluster required)
- `--previous` log support for CrashLoopBackOff cases
- Container targeting for multi-container pods

## Install
```bash
pip install k8s-ai-cli
```

## PyPI
https://pypi.org/project/k8s-ai-cli/

## Roadmap
- Include more Kubernetes context signals (events/describe output)
- Expand remediation playbooks by failure class
- Add CI-friendly output modes for automation workflows
