from datetime import datetime, UTC
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, func

from app.models import Account


class TransactionType(str, Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    transfer = "transfer"


class Transaction(SQLModel, table=True):
    """
    Transaction
    - id: Identificador único da transação
    - source_account_id: Conta de origem (pode ser nula em depósito)
    - destination_account_id: Conta de destino (pode ser nula em saque)
    - transaction_type: Tipo da transação
    - amount: Valor transferido (> 0)
    - description: Texto opcional explicando a transação
    - created_at: Momento em que a transação foi criada
    """

    id: int = Field(primary_key=True)
    source_account_id: int | None = Field(
        default=None,
        foreign_key="account.id",
        index=True,
    )
    destination_account_id: int | None = Field(
        default=None,
        foreign_key="account.id",
        index=True,
    )
    transaction_type: TransactionType = Field(nullable=False)
    amount: float = Field(nullable=False, gt=0)
    description: str | None = None
    created_at: datetime = Field(default=func.now(tz=UTC))

    source_account: Account | None = Relationship(
        back_populates="transactions_sent",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.source_account_id]",
        },
    )
    destination_account: Account | None = Relationship(
        back_populates="transactions_received",
        sa_relationship_kwargs={
            "foreign_keys": "[Transaction.destination_account_id]",
        },
    )
