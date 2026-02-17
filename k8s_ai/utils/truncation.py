from __future__ import annotations


def smart_truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False

    # Keep both head and tail to preserve startup errors and latest failure context.
    head_ratio = 0.45
    head_count = int(max_chars * head_ratio)
    tail_count = max_chars - head_count - 80

    head = text[:head_count]
    tail = text[-tail_count:] if tail_count > 0 else ""
    marker = "\n\n... [TRUNCATED MIDDLE SECTION] ...\n\n"
    return head + marker + tail, True
