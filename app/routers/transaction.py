from fastapi import APIRouter, Depends, status

from app.schemas import CreateTransaction, ShowTransaction
from app.services import TransactionService
from app.database import SessionDep

from app.routers.auth import login_user

transfer_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    dependencies=[Depends(login_user)],
)
transfer_service = TransactionService()


@transfer_router.post(
    "/",
    response_model=ShowTransaction,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transfer_in: CreateTransaction,
    session: SessionDep,
):
    return await transfer_service.create_transaction(
        transaction=transfer_in,
        session=session,
    )


@transfer_router.get("/{transaction_id}", response_model=ShowTransaction)
async def get_transaction(transfer_id: str, session: SessionDep):
    return await transfer_service.read_transaction(
        transaction_id=transfer_id,
        session=session,
    )


@transfer_router.get("/", response_model=list[ShowTransaction])
async def list_transactions(
    session: SessionDep,
    account_id: str,
    limit: int = 100,
    skip: int = 0,
):
    return await transfer_service.list_transactions(
        session=session,
        account_id=account_id,
        limit=limit,
        skip=skip,
    )


@transfer_router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reverse_transaction(transfer_id: str, session: SessionDep):
    return await transfer_service.reverse_transaction(
        transaction_id=transfer_id,
        session=session,
    )
