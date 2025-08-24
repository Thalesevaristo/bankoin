from fastapi import APIRouter, status, Depends

from app.models.user import User, UserStatus
from app.schemas import CreateUser, ShowUser, UpdateUser
from app.services import AuthService, UserService
from app.database import SessionDep

user_router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()

auth_service = AuthService()


@user_router.post(
    "/",
    response_model=ShowUser,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user_data: CreateUser, session: SessionDep):
    return await user_service.create_user(
        user=user_data,
        session=session,
    )


@user_router.get("/{user_id}", response_model=ShowUser)
async def read_user(user_id: str, session: SessionDep):
    return await user_service.read_user(
        user_id=user_id,
        session=session,
    )


@user_router.get("/", response_model=list[ShowUser])
async def list_users(
    session: SessionDep,
    username: str | None = None,
    email: str | None = None,
    status: UserStatus | None = None,
    limit: int = 100,
    skip: int = 0,
):
    return await user_service.list_users(
        session=session,
        username=username,
        email=email,
        status=status,
        limit=limit,
        skip=skip,
    )


@user_router.patch("/{user_id}", response_model=ShowUser)
async def update_user(user_id: str, user: UpdateUser, session: SessionDep):
    return await user_service.update_user(
        user_id=user_id,
        user=user,
        session=session,
    )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, session: SessionDep):
    return await user_service.delete_user(
        user_id=user_id,
        session=session,
    )


@user_router.get("/me", response_model=ShowUser)
async def read_user_me(
    current_user: User = Depends(auth_service.get_current_user),
):
    return await user_service.read_user_me(
        current_user=current_user,
    )
