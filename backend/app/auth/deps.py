from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.enums import RoleName
from app.repositories.user_repo import UserRepository
from app.utils.errors import forbidden, unauthorized

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
    except Exception:
        raise unauthorized("Invalid token")
    if payload.get("type") != "access":
        raise unauthorized("Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise unauthorized("Invalid token subject")
    user = UserRepository(db).get_by_id(int(user_id))
    if not user or not user.is_active:
        raise unauthorized("User not found or inactive")
    return user


def get_optional_user(db: Session = Depends(get_db), token: str | None = Depends(oauth2_optional_scheme)):
    if not token:
        return None
    try:
        payload = decode_token(token)
    except Exception:
        return None
    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = UserRepository(db).get_by_id(int(user_id))
    if not user or not user.is_active:
        return None
    return user


def require_roles(*roles: RoleName):
    def _dep(user=Depends(get_current_user)):
        if user.role is None:
            raise forbidden("Insufficient role")
        user_role = str(user.role.name).upper()
        allowed = {r.value if isinstance(r, RoleName) else str(r) for r in roles}
        allowed = {str(x).upper() for x in allowed}
        if user_role not in allowed:
            raise forbidden("Insufficient role")
        return user

    return _dep
