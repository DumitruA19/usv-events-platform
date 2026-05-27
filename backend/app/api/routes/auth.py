from __future__ import annotations

import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
import httpx

from app.auth.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.integrations.registry import get_integrations
from app.schemas.auth import LoginRequest, MockGoogleLoginRequest, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService
from app.utils.oauth_state import sign_state, verify_state

router = APIRouter()

def _debug_log(*args) -> None:
    # Avoid console noise in production.
    if settings.env.lower() in ("prod", "production"):
        return
    print(*args)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    out = svc.login_username_password(payload.username, payload.password)
    db.commit()
    return out


@router.post("/mock-google-login", response_model=TokenResponse)
def mock_google_login(payload: MockGoogleLoginRequest, db: Session = Depends(get_db)):
    # Production: students must use real Google OAuth flow.
    if settings.integrations_mode == "real":
        raise HTTPException(status_code=404, detail="Not found")
    svc = AuthService(db)
    out = svc.mock_google_login(payload.email)
    db.commit()
    return out


@router.get("/google/start")
def google_start(next: str = Query("/student"), db: Session = Depends(get_db)):
    _ = db
    if settings.integrations_mode != "real":
        raise HTTPException(
            status_code=501,
            detail="Real Google OAuth is disabled. Set INTEGRATIONS_MODE=real and GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET.",
        )
    try:
        integ = get_integrations()["google_oauth"]
    except Exception:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth is not configured. Set INTEGRATIONS_MODE=real and GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET.",
        )

    state = sign_state({"next": next})
    url = integ.build_authorization_url(state)
    return RedirectResponse(url=url, status_code=302)


@router.get("/google/callback")
def google_callback(code: str | None = None, state: str | None = None, db: Session = Depends(get_db)):
    if settings.integrations_mode != "real":
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_disabled", status_code=302)
    if not code or not state:
        # Google can return error=... as well; for now keep it simple.
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_failed", status_code=302)

    try:
        st = verify_state(state)
        next_path = str(st.get("next") or "/student")
    except ValueError:
        next_path = "/student"

    integ = get_integrations()["google_oauth"]
    try:
        token_payload = integ.exchange_code(code)
    except httpx.HTTPStatusError as e:
        # Do not leak secrets; surface a stable error code to the SPA and log server-side.
        _debug_log("Google OAuth token exchange failed:", e.response.status_code, e.response.text)
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_exchange_failed", status_code=302)
    except Exception as e:
        _debug_log("Google OAuth token exchange failed:", repr(e))
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_exchange_failed", status_code=302)
    access_token = token_payload.get("access_token")
    refresh_token = token_payload.get("refresh_token")
    scopes = token_payload.get("scope")
    if not access_token:
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=no_access_token", status_code=302)

    svc = AuthService(db)
    try:
        out = svc.google_oauth_login(
            access_token=str(access_token),
            refresh_token=str(refresh_token) if refresh_token else None,
            scopes=str(scopes) if scopes else None,
        )
    except httpx.HTTPStatusError as e:
        _debug_log("Google OAuth userinfo failed:", e.response.status_code, e.response.text)
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_userinfo_failed", status_code=302)
    except HTTPException as e:
        # Domain restriction / validation errors should be shown as a stable code.
        _debug_log("Google OAuth login rejected:", e.detail)
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_rejected", status_code=302)
    except OperationalError as e:
        _debug_log("Google OAuth DB failed:", repr(e))
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_db_unreachable", status_code=302)
    except Exception as e:
        _debug_log("Google OAuth login failed:", repr(e))
        return RedirectResponse(url=f"{settings.frontend_base_url}/login/student?error=oauth_login_failed", status_code=302)
    db.commit()

    # If the caller didn't pass a role-specific `next`, route by role.
    role = str(out.get("role") or "").upper()
    if role == "ADMIN":
        next_path = "/admin"
    elif role == "ORGANIZER":
        next_path = "/organizer"
    else:
        next_path = "/student"

    # Send tokens back to the SPA through a URL fragment to avoid query-string logging.
    frag = urllib.parse.urlencode(
        {
            "access_token": out["access_token"],
            "refresh_token": out["refresh_token"],
            "role": out["role"],
            "next": next_path,
        }
    )
    return RedirectResponse(url=f"{settings.frontend_base_url}/auth/callback#{frag}", status_code=302)


@router.get("/google/status")
def google_status(user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.repositories.oauth_repo import OAuthAccountRepository

    oauth = OAuthAccountRepository(db)
    acct = oauth.get_by_user(user.id, "google")
    return {"connected": bool(acct and acct.refresh_token), "email": acct.email if acct else None, "scopes": acct.scopes if acct else None}


@router.post("/google/disconnect")
def google_disconnect(user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.repositories.oauth_repo import OAuthAccountRepository

    oauth = OAuthAccountRepository(db)
    acct = oauth.get_by_user(user.id, "google")
    if acct:
        acct.refresh_token = None
        acct.scopes = None
        db.flush()
        db.commit()
    return {"status": "disconnected"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    out = svc.refresh(payload.refresh_token)
    db.commit()
    return out


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "username": user.username, "role": user.role.name}
