from contextlib import asynccontextmanager
from typing import Type
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError

from app.database import create_db_and_tables
from app.exceptions import (
    AccountNotFoundError,
    BusinessError,
    CredentialsError,
    TokenRevokedError,
    UserNotFoundError,
)
from app.routers.account import account_router
from app.routers.auth import auth_router
from app.routers.transaction import transfer_router
from app.routers.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


tags_metadata = [
    {
        "name": "Auth",
        "description": "Operations for authentication.",
    },
    {
        "name": "Accounts",
        "description": "Operations to maintain accounts.",
    },
    {
        "name": "Transactions",
        "description": "Operations to maintain transactions.",
    },
    {
        "name": "Users",
        "description": "Operations to maintain users.",
    },
]

description = "Bankoin is a API for current account transactions."


app = FastAPI(
    title="Bankoin",
    version="1.0.0",
    summary="Microservice to simulate a mini-bank.",
    description=description,
    openapi_tags=tags_metadata,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account_router)
app.include_router(auth_router)
app.include_router(transfer_router)
app.include_router(user_router)


# Centralized mapping of exceptions to responses
EXCEPTION_HANDLERS: dict[Type[Exception], tuple[int, str | None]] = {
    AccountNotFoundError: (status.HTTP_404_NOT_FOUND, "Account not found."),
    BusinessError: (status.HTTP_409_CONFLICT, None),
    CredentialsError: (status.HTTP_401_UNAUTHORIZED, "Invalid credentials"),
    InvalidTokenError: (status.HTTP_401_UNAUTHORIZED, "Invalid token"),
    TokenRevokedError: (status.HTTP_401_UNAUTHORIZED, "Token revoked"),
    UserNotFoundError: (status.HTTP_401_UNAUTHORIZED, "User not found"),
}


def create_exception_handler(
    status_code: int,
    default_message: str | None = None,
):
    async def handler(request: Request, exc: Exception):
        message = str(exc) if default_message is None else default_message
        return JSONResponse(
            status_code=status_code,
            content={"detail": message},
        )

    return handler


# Register all handlers dynamically
for exc_class, (status_code, message) in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(
        exc_class,
        create_exception_handler(status_code, message),
    )


@app.get("/")
async def root():
    return {"status": "ok"}
