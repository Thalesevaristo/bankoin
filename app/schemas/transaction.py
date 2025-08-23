from pydantic import AwareDatetime, BaseModel, Field

from app.models import TransactionType


# Entrada
class CreateTransaction(BaseModel):
    source_account_id: int | None = None
    destination_account_id: int | None = None
    type: TransactionType
    amount: float = Field(..., gt=0)
    description: str | None = None


# Saída
class ShowTransaction(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    type: TransactionType
    amount: float
    description: str | None = None
    created_at: AwareDatetime
