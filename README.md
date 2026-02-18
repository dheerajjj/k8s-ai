# k8s-ai

A Python CLI for Kubernetes pod failure triage using AI-powered log analysis.

## Features

- Reads pod logs directly through your local `kubectl` context
- Uses OpenAI Python SDK v1.x for log analysis
- Returns likely root cause, confidence level, and remediation guidance
- Supports `--mock`, `--previous`, `--container`, and `--timeout`

## Installation

```bash
pip install k8s-ai-cli
```

## Quick Start

```bash
k8s-ai default my-pod
k8s-ai default my-pod --mock
k8s-ai default my-pod --previous
k8s-ai default my-pod --container app
```

## Mock Example

```bash
k8s-ai default my-pod --mock
```

## Real Cluster Example

```bash
# Current pod logs
k8s-ai default my-pod

# Previous logs (useful for CrashLoopBackOff)
k8s-ai default my-pod --previous

# Target a specific container
k8s-ai default my-pod --container app
```

## Environment Variables

`k8s-ai` requires an OpenAI API key.

Linux/macOS:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

## How It Works

1. Collects logs for the target pod using `kubectl`.
2. Sends relevant log context to an OpenAI-compatible model (OpenAI SDK v1.x).
3. Produces structured output with probable cause, confidence, and remediation steps.

## Safety

- Runs locally on your machine.
- Uses your current `kubectl` permissions and context.
- Does not persist collected pod logs by default.

## Roadmap

- Broader failure-pattern coverage for common Kubernetes workloads
- Optional structured output modes for CI and automation
- Additional debugging context integration (events/describe)

## License

MIT

