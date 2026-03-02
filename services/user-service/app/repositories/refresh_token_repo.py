import hashlib
from datetime import datetime, timezone

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class RefreshTokenRepository(BaseRepository):
    def create(
            self,
            user_id: int,
            token: str,
            jti: str,
            expires_at: datetime,
            user_agent: str | None = None,
            ip_address: str | None = None,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(token),
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        self.db.add(refresh_token)
        return refresh_token
    
    def get_by_jti(self, jti: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jti == jti)
            .first()
        )
    
    def get_by_token(self, token: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == hash_token(token))
            .first()
        )
    
    def revoke(self, refresh_token: RefreshToken) -> RefreshToken:
        # Mark the token as revoked and commit the change to the database
        refresh_token.revoked = True
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token
    
    def revoke_all_for_user(self, user_id: int) -> None:
        # Revoke all refresh tokens for the specified user
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
        ).update({"revoked": True})
        self.db.commit()

    def delete_expired_tokens(self, user_id: int) -> None:
        # Delete all expired refresh tokens for the specified user
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.expires_at < datetime.now(timezone.utc),
        ).delete()
        self.db.commit()

    def get_active_sessions(self, user_id: str) -> list[RefreshToken]:
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
            .order_by(RefreshToken.created_at.desc())
            .all()
        )