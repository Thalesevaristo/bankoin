from pathlib import Path
from urllib import parse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # === Security Settings ===
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Database Settings ===
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int = 5432
    DATABASE_HOST: str = "localhost"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignora variáveis não declaradas
    )

    @property
    def DATABASE_URL(self) -> str:
        password = parse.quote_plus(self.DATABASE_PASSWORD)
        return (
            f"postgresql+psycopg://{self.DATABASE_USER}:{password}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


# === Singleton Settings Instance ===
settings = Settings()
