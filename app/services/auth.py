from datetime import datetime, timedelta, UTC

import jwt

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select

from app.database import SessionDep
from app.models import User
from app.schemas import TokenResponse, TokenStore
from app.security import verify_password
from app.settings import settings

# Exceções comuns reutilizáveis
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)

INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
)

TOKEN_REVOKED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token revoked",
)

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)


class AuthService:
    """Serviço responsável pela autenticação e gestão de tokens JWT."""

    # --------------------
    # Gestão de JWT
    # --------------------
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Cria um token JWT com tempo de expiração definido."""
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta
            or timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica e valida um token JWT."""
        try:
            return jwt.decode(
                token,
                key=settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        except jwt.InvalidTokenError:
            raise INVALID_TOKEN_EXCEPTION

    # --------------------
    # Fluxos de autenticação
    # --------------------
    async def login_user(
        self,
        session: SessionDep,
        login_data: OAuth2PasswordRequestForm,
    ) -> TokenResponse:
        """Autentica um usuário e retorna um novo token de acesso."""
        query = select(User).where(User.username == login_data.username)
        user = session.exec(query).first()

        if not user or not verify_password(
            login_data.password,
            user.password,
        ):
            raise CREDENTIALS_EXCEPTION

        return await self.refresh_token(user)

    async def refresh_token(self, user: User) -> TokenResponse:
        """Gera um novo token JWT para o usuário autenticado."""
        access_token = self.create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_current_user(
        self,
        session: SessionDep,
        token: str,
    ) -> User:
        """Recupera o usuário atual a partir de um token válido."""
        payload = self.decode_token(token)
        user_id: str | None = payload.get("sub")

        if not user_id:
            raise INVALID_TOKEN_EXCEPTION
        if TokenStore.is_revoked(user_id):
            raise TOKEN_REVOKED_EXCEPTION

        user = session.get(User, user_id)
        if not user:
            raise USER_NOT_FOUND_EXCEPTION

        return user

    async def logout(
        self,
        token: str,
        session: SessionDep,
    ) -> dict:
        """Realiza logout do usuário, invalidando seu token JWT."""
        payload = self.decode_token(token)
        user_id: str | None = payload.get("sub")

        if not user_id:
            raise INVALID_TOKEN_EXCEPTION

        user = session.get(User, user_id)
        if not user:
            raise USER_NOT_FOUND_EXCEPTION

        TokenStore.revoke(user_id)
        return {"msg": "Logout realizado com sucesso"}
