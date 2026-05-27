from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    # bcrypt has a 72-byte input limit; enforce explicitly to avoid surprising truncation.
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password too long for bcrypt (max 72 bytes)")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def _normalize_hash(hashed_password: str) -> str:
    # Common cleanup for DB-stored strings.
    h = (hashed_password or "").strip()
    # Handle accidental Python-bytes repr: b'...'
    if (h.startswith("b'") and h.endswith("'")) or (h.startswith('b"') and h.endswith('"')):
        h = h[2:-1]
    return h


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_bytes = plain_password.encode("utf-8")
        h = _normalize_hash(hashed_password)
        hashed_bytes = h.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False
