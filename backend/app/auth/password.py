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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False
