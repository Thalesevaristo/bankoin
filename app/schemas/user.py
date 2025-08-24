from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from app.models import UserAccess, UserStatus
from app.security import get_password_hash


# Entrada
class CreateUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    email: EmailStr
    first_name: str = Field(..., max_length=15)
    last_name: str = Field(..., max_length=15)

    @field_validator("password")
    def hash_password(cls, v: str) -> str:
        return get_password_hash(v)


# Entrada
class UpdateUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    password: str | None = Field(default=None, min_length=8)
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=15)
    last_name: str | None = Field(default=None, max_length=15)
    permission: UserAccess | None = None
    status: UserStatus | None = None

    @field_validator("password")
    def hash_password(cls, v: str) -> str:
        return get_password_hash(v)


# Saída
class ShowUser(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    permission: UserAccess
    status: UserStatus
    created_at: AwareDatetime
