from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
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


@app.get("/")
async def root():
    return {"status": "ok"}
