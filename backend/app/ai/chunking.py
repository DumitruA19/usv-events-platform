from __future__ import annotations


def chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 150) -> list[str]:
    t = (text or "").strip()
    if not t:
        return []
    if max_chars <= 0:
        return [t]
    overlap = max(0, overlap)

    out: list[str] = []
    i = 0
    while i < len(t):
        j = min(len(t), i + max_chars)
        out.append(t[i:j].strip())
        if j >= len(t):
            break
        i = max(0, j - overlap)
    return [c for c in out if c]

