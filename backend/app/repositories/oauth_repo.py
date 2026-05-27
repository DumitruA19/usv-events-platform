from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.oauth_account import OAuthAccount


class OAuthAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int, provider: str) -> OAuthAccount | None:
        return self.db.scalar(select(OAuthAccount).where(OAuthAccount.user_id == user_id, OAuthAccount.provider == provider))

    def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> OAuthAccount | None:
        return self.db.scalar(
            select(OAuthAccount).where(OAuthAccount.provider == provider, OAuthAccount.provider_user_id == provider_user_id)
        )

    def upsert_google(
        self,
        *,
        user_id: int,
        provider_user_id: str,
        email: str | None,
        scopes: str | None,
        refresh_token: str | None,
    ) -> OAuthAccount:
        acct = self.get_by_user(user_id, "google")
        if not acct:
            acct = OAuthAccount(
                user_id=user_id,
                provider="google",
                provider_user_id=provider_user_id,
                email=email,
                scopes=scopes,
                refresh_token=refresh_token,
            )
            self.db.add(acct)
            self.db.flush()
            return acct

        acct.provider_user_id = provider_user_id
        acct.email = email
        acct.scopes = scopes
        # Google may omit refresh_token on subsequent logins; keep the existing one.
        if refresh_token:
            acct.refresh_token = refresh_token
        self.db.flush()
        return acct

