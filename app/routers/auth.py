from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from app.models import User
from app.schemas import TokenResponse, ShowUser
from app.services import AuthService
from app.database import SessionDep

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Autentica o usuário e retorna um token JWT.
    """
    return await auth_service.login_user(
        session=session,
        login_data=form_data,
    )


@auth_router.get(
    "/refresh/{account_id}",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(account_id: str, session: SessionDep):
    """
    Gera um novo token para o usuário informado.
    """
    user = session.get(User, account_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return await auth_service.refresh_token(user=user)


@auth_router.get(
    "/me",
    response_model=ShowUser,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
):
    """
    Retorna os dados do usuário atual com base no token JWT.
    """
    return await auth_service.get_current_user(
        token=token,
        session=session,
    )


@auth_router.delete(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    session: SessionDep,
    token: str,
):
    """
    Realiza logout do usuário, invalidando o token.
    """
    return await auth_service.logout(
        token=token,
        session=session,
    )
