from __future__ import annotations

from sqlalchemy.orm import Session

from app.auth.password import verify_password
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.integrations.registry import get_integrations
from app.models.enums import RoleName
from app.models.profiles import StudentProfile
from app.models.role import Role
from app.models.user import User
from app.repositories.oauth_repo import OAuthAccountRepository
from app.repositories.user_repo import UserRepository
from app.utils.errors import bad_request, unauthorized
from app.core.config import allowed_student_email_domains


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.oauth = OAuthAccountRepository(db)

    def _ensure_role(self, role_name: RoleName) -> Role:
        role = self.db.query(Role).filter(Role.name == role_name.value).one_or_none()
        if role:
            return role
        role = Role(name=role_name.value)
        self.db.add(role)
        self.db.flush()
        return role

    def login_username_password(self, username: str, password: str) -> dict:
        user = self.users.get_by_username(username)
        if not user or not user.is_active or not user.hashed_password:
            raise unauthorized("Invalid credentials")
        if not verify_password(password, user.hashed_password):
            raise unauthorized("Invalid credentials")
        if user.role and user.role.name == RoleName.STUDENT.value:
            # Students must use Google OAuth only (no password login).
            raise unauthorized("Invalid credentials")
        return self._tokens_for_user(user)

    def mock_google_login(self, email: str) -> dict:
        integ = get_integrations()["google_oauth"]
        try:
            info = integ.mock_login(email)
        except ValueError as e:
            raise bad_request(str(e))

        user = self.users.get_by_email(info.email)
        if user and not user.is_active:
            raise unauthorized("User inactive")

        if not user:
            # Student user has no password; login via mock OAuth only.
            role = self._ensure_role(RoleName.STUDENT)
            user = User(email=info.email, username=None, hashed_password=None, role_id=role.id, is_active=True)
            self.users.add(user)
            self.db.add(StudentProfile(user_id=user.id, full_name=info.full_name))
            self.db.flush()

        return self._tokens_for_user(user)

    def google_oauth_login(self, *, access_token: str, refresh_token: str | None, scopes: str | None) -> dict:
        """Login/Signup using real Google OAuth (userinfo endpoint)."""
        integ = get_integrations()["google_oauth"]
        info = integ.fetch_userinfo(access_token)

        email = (info.get("email") or "").strip().lower()
        if not email:
            raise bad_request("Google account has no email")
        if info.get("email_verified") is False:
            raise bad_request("Google email is not verified")
        domains = allowed_student_email_domains()
        is_student_email = bool(domains) and any(email.endswith("@" + d) for d in domains)

        provider_user_id = str(info.get("sub") or "")
        if not provider_user_id:
            raise bad_request("Google userinfo missing subject")

        full_name = info.get("name")

        # Prefer linking by Google subject to avoid duplicate accounts / unique constraint issues.
        existing_oauth = self.oauth.get_by_provider_user_id("google", provider_user_id)
        user = self.users.get_by_id(existing_oauth.user_id) if existing_oauth else None
        if not user:
            user = self.users.get_by_email(email)
        if user and not user.is_active:
            raise unauthorized("User inactive")

        if not user:
            if not is_student_email:
                # Allow Google login for organizer/admin only if the account already exists.
                raise unauthorized("Account not allowed")
            role = self._ensure_role(RoleName.STUDENT)
            user = User(email=email, username=None, hashed_password=None, role_id=role.id, is_active=True)
            self.users.add(user)
            self.db.add(StudentProfile(user_id=user.id, full_name=full_name))
            self.db.flush()
        else:
            # Existing user: enforce student domain for student role; never auto-upgrade roles.
            if user.role and user.role.name == RoleName.STUDENT.value and not is_student_email:
                raise unauthorized("Account not allowed")
            if user.role and user.role.name in (RoleName.ORGANIZER.value, RoleName.ADMIN.value) and is_student_email:
                # Avoid role confusion for institutional emails.
                raise unauthorized("Account not allowed")

        self.oauth.upsert_google(
            user_id=user.id,
            provider_user_id=provider_user_id,
            email=email,
            scopes=scopes,
            refresh_token=refresh_token,
        )

        return self._tokens_for_user(user)

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise unauthorized("Invalid refresh token")
        if payload.get("type") != "refresh":
            raise unauthorized("Invalid refresh token type")
        sub = payload.get("sub")
        if not sub:
            raise unauthorized("Invalid refresh token subject")
        user = self.users.get_by_id(int(sub))
        if not user or not user.is_active:
            raise unauthorized("User not found or inactive")
        return self._tokens_for_user(user)

    def _tokens_for_user(self, user: User) -> dict:
        role = RoleName(user.role.name)
        access = create_access_token(str(user.id), role.value)
        refresh = create_refresh_token(str(user.id), role.value)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "role": role.value,
            "user": {"id": user.id, "email": user.email, "username": user.username, "role": role.value},
        }
