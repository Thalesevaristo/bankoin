from sqlmodel import select

from app.exceptions import AccountNotFoundError
from app.models import Account
from app.schemas import CreateAccount, ShowAccount, UpdateAccount
from app.database import SessionDep


class AccountService:

    async def create_account(
        self,
        account: CreateAccount,
        session: SessionDep,
    ) -> ShowAccount:
        db_account = Account(**account.model_dump())
        session.add(db_account)
        session.commit()
        session.refresh(db_account)
        return ShowAccount.model_validate(db_account.model_dump())

    async def read_account(
        self,
        account_id: str,
        session: SessionDep,
    ) -> ShowAccount:
        account = session.get(Account, account_id)
        if not account:
            raise AccountNotFoundError
        return ShowAccount.model_validate(account.model_dump())

    async def list_accounts(
        self,
        session: SessionDep,
        user_id: str | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[ShowAccount]:
        query = select(Account).limit(limit).offset(skip)
        if user_id is not None:
            query = query.where(Account.user_id == user_id)
        accounts = session.exec(query).all()
        return [ShowAccount.model_validate(a.model_dump()) for a in accounts]

    async def update_account(
        self,
        account_id: int,
        account: UpdateAccount,
        session: SessionDep,
    ) -> ShowAccount:
        db_account = session.get(Account, account_id)
        if not db_account:
            raise AccountNotFoundError

        for key, value in account.model_dump(exclude_unset=True).items():
            setattr(db_account, key, value)

        session.add(db_account)
        session.commit()
        session.refresh(db_account)
        return ShowAccount.model_validate(db_account.model_dump())

    async def delete_account(self, account_id: str, session: SessionDep):
        db_account = session.get(Account, account_id)
        if not db_account:
            raise AccountNotFoundError
        session.delete(db_account)
        session.commit()
        return {"ok": True}
