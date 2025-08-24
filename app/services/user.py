from fastapi import HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import User, UserStatus
from app.schemas import CreateUser, ShowUser, UpdateUser


class UserService:

    async def create_user(
        self,
        user: CreateUser,
        session: SessionDep,
    ) -> ShowUser:
        """Cria um novo usuário."""
        db_user = User(**user.model_dump())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return ShowUser.model_validate(db_user.model_dump())

    async def read_user(
        self,
        user_id: str,
        session: SessionDep,
    ) -> ShowUser:
        """Busca um usuário pelo ID."""
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return ShowUser.model_validate(db_user.model_dump())

    async def list_users(
        self,
        session: SessionDep,
        username: str | None = None,
        email: str | None = None,
        status: UserStatus | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[ShowUser]:
        """
        Lista usuários com base em critérios opcionais.
        - username: Nome de usuário (pode ser parcial)
        - email: E-mail (pode ser parcial)
        - status: Se o usuário está (ativo, inativo ou suspenso)
        - limit: Máximo de resultados
        - skip: Quantidade de registros a pular (paginação)
        """
        query = select(User).limit(limit).offset(skip)

        if username:
            query = query.where(username in User.username)
        if email:
            query = query.where(email in User.email)
        if status is not None:
            query = query.where(User.status == status)

        users = session.exec(query).all()
        return [ShowUser.model_validate(u.model_dump()) for u in users]

    async def update_user(
        self,
        user_id: str,
        user: UpdateUser,
        session: SessionDep,
    ) -> ShowUser:
        """Atualiza os dados de um usuário pelo ID."""
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        data_user = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(data_user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return ShowUser.model_validate(db_user.model_dump())

    async def delete_user(
        self,
        user_id: str,
        session: SessionDep,
    ) -> dict[str, bool]:
        """Remove um usuário pelo ID."""
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        session.delete(db_user)
        session.commit()
        return {"ok": True}

    async def read_user_me(self, current_user: User):
        return current_user
