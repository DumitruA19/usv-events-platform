from __future__ import annotations

import re


_WS = re.compile(r"[ \t]+")
_NL = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    t = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    t = _WS.sub(" ", t)
    t = _NL.sub("\n\n", t)
    return t.strip()

