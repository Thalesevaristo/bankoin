from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenStore:
    _revoked_tokens: set[str] = set()

    @classmethod
    def revoke(cls, user_id: str):
        cls._revoked_tokens.add(user_id)

    @classmethod
    def is_revoked(cls, user_id: str) -> bool:
        return user_id in cls._revoked_tokens
