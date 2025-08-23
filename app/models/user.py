from datetime import datetime, UTC
from enum import Enum
from uuid import uuid4

from pydantic import UUID4, EmailStr
from sqlmodel import SQLModel, Field, Relationship, func

from app.models import Account


class UserAccess(str, Enum):
    client = "client"
    manager = "manager"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class User(SQLModel, table=True):
    """
    User
    - id: Identificador único do usuário
    - username: Identificador único do usuário para identificação e login
    - password: Armazena a versão hash da senha do usuário
    - email: Endereço de e-mail único do usuário
    - first_name / last_name: Os nomes de batismo e sobrenome do usuário
    - permission: Nível de acesso do usuário dentro do aplicativo
    - status: O estado atual do usuário (ativo, inativo, suspenso)
    - created_at: Momento em que o usuário foi registrado no sistema
    """

    id: UUID4 = Field(default_factory=uuid4, primary_key=True)

    username: str = Field(
        index=True,
        unique=True,
        nullable=False,
        max_length=30,
    )
    password: str = Field(nullable=False)

    email: EmailStr = Field(unique=True, nullable=False)
    first_name: str = Field(nullable=False, max_length=15)
    last_name: str = Field(nullable=False, max_length=15)
    permission: UserAccess = Field(default=UserAccess.client)
    status: UserStatus = Field(default=UserStatus.active)
    created_at: datetime = Field(default=func.now(tz=UTC))

    accounts: list[Account] = Relationship(back_populates="owner")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
