import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.users import User
from app.repositories.auth_repo import AuthRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, auth_repo: AuthRepository, token_repo: RefreshTokenRepository):
        self.auth_repo = auth_repo
        self.token_repo = token_repo

    def register_user(
            self, 
            email: str, 
            hashed_password: str, 
            username: str,
            user_agent: str | None = None,
            ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        if self.auth_repo.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        if self.auth_repo.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
       
        user = self.auth_repo.create_user(
            email=email,
            hashed_password=hashed_password,
            username=username
        )
        self.auth_repo.db.commit()
        self.auth_repo.db.refresh(user)
       
        access_token, refresh_token = self._issue_tokens(
            user, user_agent=user_agent, ip_address=ip_address
            )
        logger.info("User registered: %s", user.id)
        return user, access_token, refresh_token


    def login_user(
            self,
            email: str,
            password: str,
            user_agent : str | None = None,
            ip_address : str | None = None,
    ) -> tuple[User, str, str]:
        user = self.auth_repo.get_user_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        self.token_repo.delete_expired_tokens(str(user.id))
        access_token, refresh_token = self._issue_tokens(user, user_agent, ip_address)
        logger.info("User logged in: %s", user.id)
        return user, access_token, refresh_token
    
    def refresh_tokens(
            self,
        refresh_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        claims = verify_token(refresh_token, expected_type="refresh")
        jti = claims.get("jti")

        db_token = self.token_repo.get_by_jti(jti)
        if not db_token or db_token.revoked:
            raise HTTPException(status_code=401, detail="Refresh token is invalid or revoked")

        user = self.auth_repo.get_user_by_id(claims.get("sub"))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        self.token_repo.revoke(db_token)
        access_token, new_refresh_token = self._issue_tokens(user, user_agent, ip_address)
        logger.info("Tokens refreshed for user: %s", user.id)
        return user, access_token, new_refresh_token

    # --- Logout ---
    def logout(self, refresh_token: str) -> None:
        claims = verify_token(refresh_token, expected_type="refresh")
        jti = claims.get("jti")
        db_token = self.token_repo.get_by_jti(jti)
        if db_token and not db_token.revoked:
            self.token_repo.revoke(db_token)
        logger.info("User logged out, jti: %s", jti)

    def logout_all(self, user_id: str) -> None:
        self.token_repo.revoke_all_for_user(user_id)
        logger.info("All sessions revoked for user: %s", user_id)

    # --- Delete / Update ---
    def delete_user(self, user_id: str) -> None:
        user = self.auth_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.auth_repo.delete_user(user)

    def update_user(self, user_id: str, **kwargs) -> User:
        user = self.auth_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if "password" in kwargs:
            kwargs["hashed_password"] = hash_password(kwargs.pop("password"))
        return self.auth_repo.update_user(user, **kwargs)

    # --- Private ---

    def _issue_tokens(
        self,
        user: User,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[str, str]:
        access_token = create_access_token(sub=str(user.id))
        refresh_token = create_refresh_token(sub=str(user.id))

        claims = verify_token(refresh_token, expected_type="refresh")
        self.token_repo.create(
            user_id=str(user.id),
            token=refresh_token,
            jti=claims["jti"],
            expires_at=datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.token_repo.commit()
        return access_token, refresh_token
    
       

