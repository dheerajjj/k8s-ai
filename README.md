# k8s-ai

CLI that explains Kubernetes pod failures from logs using AI.

## Features
- Collects logs from Kubernetes pods via `kubectl`
- AI-powered root-cause analysis (OpenAI-compatible API)
- Detects common failure classes:
  - CrashLoopBackOff
  - OOMKilled
  - ImagePullBackOff
  - DB connection timeout/errors
  - Permission denied / RBAC-style issues
  - HTTP 500 style failures
- Suggests remediation steps and safe `kubectl` follow-up commands
- Supports multi-container pods and `--previous` logs
- Offline `--mock` mode (no kubectl calls required)
- Sensitive data redaction before model input

## Project Structure
```text
k8s_ai/
├── .env.example
├── pyproject.toml
├── requirements.txt
├── README.md
└── k8s_ai/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── config.py
    ├── models.py
    ├── logging_setup.py
    ├── collector/
    ├── analyzer/
    ├── fixer/
    └── utils/
```

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` values:
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`

## Usage

Analyze pod:
```powershell
python -m k8s_ai analyze <namespace> <pod>
```

Analyze specific container:
```powershell
python -m k8s_ai analyze <namespace> <pod> --container <container-name>
```

Use previous container logs:
```powershell
python -m k8s_ai analyze <namespace> <pod> --previous
```

Run fully offline:
```powershell
python -m k8s_ai analyze default dummy-pod --mock
```

## Notes
- In non-mock mode, `kubectl` and cluster access are required.
- In mock mode, realistic sample logs are used and no kubectl command is executed.

## License
MIT
# Kubernetes Log Analyzer Agent

AI-powered CLI tool to collect Kubernetes pod logs and perform root-cause analysis with safe, structured remediation guidance.

## Features

- Analyze logs for any namespace/pod
- Multi-container pod support
- Previous container logs (`--previous`)
- Timeout handling
- Intelligent log truncation
- Secret redaction before LLM call
- Optional suggested `kubectl` fix commands
- Offline mock mode for testing without API calls
- Rich terminal output

## Project Structure

```text
k8s_ai/
├── .env.example
├── requirements.txt
├── README.md
└── k8s_ai/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── config.py
    ├── models.py
    ├── logging_setup.py
    ├── collector/
    │   ├── __init__.py
    │   └── kubectl_collector.py
    ├── analyzer/
    │   ├── __init__.py
    │   └── llm_analyzer.py
    ├── fixer/
    │   ├── __init__.py
    │   └── command_generator.py
    └── utils/
        ├── __init__.py
        ├── redaction.py
        └── truncation.py
```

