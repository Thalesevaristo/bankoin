from fastapi import HTTPException
from sqlmodel import select, or_

from app.database import SessionDep
from app.models import Transaction, Account
from app.schemas import CreateTransaction, ShowTransaction


class TransactionService:

    async def create_transaction(
        self, transaction: CreateTransaction, session: SessionDep
    ) -> ShowTransaction:
        """
        Cria uma transação (depósito, saque ou transferência)
        - Se apenas destination_account_id for informado => depósito
        - Se apenas source_account_id for informado => saque
        - Se ambos forem informados => transferência
        """

        if transaction.amount <= 0:
            raise ValueError("O valor da transação deve ser positivo.")

        # Se for saque ou transferência: precisa validar saldo
        if transaction.source_account_id:
            source_account = session.get(
                Account,
                transaction.source_account_id,
            )
            if not source_account:
                raise ValueError("Conta de origem não encontrada.")
            if source_account.balance < transaction.amount:
                raise ValueError(
                    "Saldo insuficiente para realizar a transação.",
                )
            source_account.balance -= transaction.amount

        # Se for depósito ou transferência: precisa adicionar ao destino
        if transaction.destination_account_id:
            destination_account = session.get(
                Account,
                transaction.destination_account_id,
            )
            if not destination_account:
                raise ValueError("Conta de destino não encontrada.")
            destination_account.balance += transaction.amount

        # Criar a transação no histórico
        transfer = CreateTransaction(
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id,
            type=transaction.type,
            amount=transaction.amount,
            description=transaction.description,
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        session.add(transfer)
        session.commit()
        session.refresh(transfer)

        return ShowTransaction.model_validate(transfer.model_dump())

    async def read_transaction(
        self, transaction_id: str, session: SessionDep
    ) -> ShowTransaction:
        transaction = session.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found",
            )
        return ShowTransaction.model_validate(transaction.model_dump())

    async def list_transactions(
        self,
        session: SessionDep,
        account_id: str | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[ShowTransaction]:
        """
        Lista transações, podendo filtrar por conta.
        - session: Sessão do banco
        - account_id: Conta para filtrar (pode ser origem ou destino)
        - limit: Quantidade máxima de resultados
        - skip: Quantidade de registros a pular (paginação)
        """
        query = select(Transaction).limit(limit).offset(skip)

        if account_id is not None:
            query = query.where(
                or_(
                    Transaction.source_account_id == account_id,
                    Transaction.destination_account_id == account_id,
                )
            )

        transactions = session.exec(query).all()

        return [ShowTransaction.
                model_validate(t.model_dump()) for t in transactions]

    async def reverse_transaction(
        self,
        transaction_id: str,
        session: SessionDep,
    ):
        """
        Estorna uma transação existente (depósito, saque ou transferência)
        - Para depósitos: subtrai do destination_account
        - Para saques: adiciona ao source_account
        - Para transferências: desfaz movimentação entre source e destination
        """

        transaction = session.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found",
            )

        empty_source = transaction.source_account_id is None
        empty_destination = transaction.destination_account_id is None
        data_source = transaction.source_account_id
        data_destination = transaction.destination_account_id

        # Depósito
        if empty_source and data_destination:
            dest_account = session.get(
                Account,
                transaction.destination_account_id,
            )
            if dest_account.balance < transaction.amount:
                raise ValueError(
                    "Saldo insuficiente na conta para estornar o depósito."
                )
            dest_account.balance -= transaction.amount

        # Saque
        elif empty_destination and data_source:
            src_account = session.get(
                Account,
                transaction.source_account_id,
            )
            src_account.balance += transaction.amount

        # Transferência
        elif data_source and data_destination:
            src_account = session.get(
                Account,
                transaction.source_account_id,
            )
            dest_account = session.get(
                Account,
                transaction.destination_account_id,
            )

            if dest_account.balance < transaction.amount:
                raise ValueError(
                    "Saldo insuficiente na conta de destino",
                    " para estornar a transferência."
                )

            src_account.balance += transaction.amount
            dest_account.balance -= transaction.amount

        else:
            raise ValueError("Transação inválida para estorno.")

        reverse_tx = CreateTransaction(
            source_account_id=transaction.destination_account_id,
            destination_account_id=transaction.source_account_id,
            type=transaction.transaction_type,
            amount=transaction.amount,
            description=f"Estorno da transação {transaction.id}",
        )

        session.add(reverse_tx)
        session.commit()
        session.refresh(reverse_tx)

        return reverse_tx
