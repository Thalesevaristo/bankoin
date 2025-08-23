from pydantic import UUID4, BaseModel


# Entrada
class CreateAccount(BaseModel):
    user_id: UUID4
    balance: float | None = 0.0


# Entrada
class UpdateAccount(BaseModel):
    balance: float | None = None


# Saída
class ShowAccount(BaseModel):
    id: int
    user_id: str
    balance: float
