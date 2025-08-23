from datetime import datetime, UTC

from pydantic import UUID4
from sqlmodel import SQLModel, Field, Relationship, func

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User, Transaction


class Account(SQLModel, table=True):
    """
    Account
    - id: Identificador único da conta
    - user_id: ID do usuário proprietário da conta
    - balance: Saldo atual da conta
    - created_at: Momento em que a conta foi criada
    """

    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id", nullable=False)
    balance: float = Field(default=0.0)
    created_at: datetime = Field(default=func.now(tz=UTC))

    owner: "User" = Relationship(back_populates="accounts")

    transactions_sent: list["Transaction"] = Relationship(
        back_populates="source_account",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.source_account_id]",
        },
    )
    transactions_received: list["Transaction"] = Relationship(
        back_populates="destination_account",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.destination_account_id]",
        },
    )

    @property
    def all_transactions(self) -> list["Transaction"]:
        return self.transactions_sent + self.transactions_received
