from __future__ import annotations

import re


SENSITIVE_PATTERNS = [
    # Generic key=value secrets
    re.compile(r"(?i)\b(password|passwd|pwd|secret|token|apikey|api_key|client_secret)\s*[:=]\s*([^\s,;]+)"),
    # Authorization Bearer tokens
    re.compile(r"(?i)\b(authorization)\s*[:=]\s*bearer\s+([a-zA-Z0-9\-\._~\+/]+=*)"),
    # AWS access key id style
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # PEM blocks
    re.compile(r"-----BEGIN [A-Z ]+-----[\s\S]*?-----END [A-Z ]+-----"),
    # URI credentials
    re.compile(r"([a-zA-Z]+:\/\/)([^:\s\/]+):([^@\s\/]+)@"),
]


def redact_sensitive_content(text: str) -> str:
    redacted = text

    def _mask_kv(match: re.Match[str]) -> str:
        key = match.group(1)
        return f"{key}=<REDACTED>"

    redacted = SENSITIVE_PATTERNS[0].sub(_mask_kv, redacted)
    redacted = SENSITIVE_PATTERNS[1].sub(r"\1: Bearer <REDACTED>", redacted)
    redacted = SENSITIVE_PATTERNS[2].sub("<REDACTED_AWS_KEY>", redacted)
    redacted = SENSITIVE_PATTERNS[3].sub("<REDACTED_PEM_BLOCK>", redacted)
    redacted = SENSITIVE_PATTERNS[4].sub(r"\1<REDACTED_USER>:<REDACTED_PASS>@", redacted)

    return redacted
