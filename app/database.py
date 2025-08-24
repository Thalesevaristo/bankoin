from typing_extensions import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from app.settings import settings

# Criação do engine usando as configs do settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # log SQL
    connect_args={"connect_timeout": 5},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# Tipo para usar em Depends nas rotas/serviços
SessionDep = Annotated[Session, Depends(get_session)]
