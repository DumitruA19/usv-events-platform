from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.core.config import settings


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))


def sign_state(payload: dict[str, Any], *, ttl_seconds: int = 600) -> str:
    now = int(time.time())
    body = dict(payload)
    body["iat"] = now
    body["exp"] = now + int(ttl_seconds)
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    sig = hmac.new(settings.oauth_state_secret_key.encode("utf-8"), raw, hashlib.sha256).digest()
    return f"{_b64url_encode(raw)}.{_b64url_encode(sig)}"


def verify_state(state: str) -> dict[str, Any]:
    try:
        raw_b64, sig_b64 = state.split(".", 1)
        raw = _b64url_decode(raw_b64)
        got_sig = _b64url_decode(sig_b64)
        exp_sig = hmac.new(settings.oauth_state_secret_key.encode("utf-8"), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(got_sig, exp_sig):
            raise ValueError("Invalid state signature")
        payload = json.loads(raw.decode("utf-8"))
        exp = int(payload.get("exp") or 0)
        if exp and int(time.time()) > exp:
            raise ValueError("State expired")
        return payload
    except Exception as e:
        raise ValueError("Invalid state") from e

