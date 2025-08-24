from fastapi import APIRouter, status

from app.schemas import ShowAccount, CreateAccount
from app.schemas.account import UpdateAccount
from app.services import AccountService

from app.database import SessionDep

account_router = APIRouter(prefix="/accounts", tags=["Accounts"])
account_service = AccountService()


@account_router.post(
    "/",
    response_model=ShowAccount,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(account_in: CreateAccount, session: SessionDep):
    return await account_service.create_account(
        account=account_in,
        session=session,
    )


@account_router.get("/{account_id}", response_model=ShowAccount)
async def get_account(account_id: str, session: SessionDep):
    return await account_service.read_account(
        account_id=account_id,
        session=session,
    )


@account_router.get("/", response_model=list[ShowAccount])
async def list_accounts(
    session: SessionDep,
    user_id: str,
    limit: int = 100,
    skip: int = 0,
):
    return await account_service.list_accounts(
        session=session,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )


@account_router.patch(
    "/{account_id}",
    response_model=ShowAccount,
    status_code=status.HTTP_200_OK,
)
async def update_account(
    account_id: int,
    account_data: UpdateAccount,
    session: SessionDep,
):
    return await account_service.update_account(
        account_id=account_id,
        account=account_data,
        session=session,
    )


@account_router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str, session: SessionDep):
    return await account_service.delete_account(
        account_id=account_id,
        session=session,
    )
