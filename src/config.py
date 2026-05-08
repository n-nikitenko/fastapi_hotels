from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DATABASE_DSN: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str
    UPLOAD_DIR: str = str(BASE_DIR.joinpath("static").joinpath("images"))
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]

    @model_validator(mode="after")
    def build_database_dsn(self) -> "Settings":
        # Prefer deterministic DSN assembled from POSTGRES_* to avoid config drift
        # between POSTGRES_DB and DATABASE_DSN values in CI/CD env files.
        postgres_parts = (
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )
        if all(part is not None for part in postgres_parts):
            self.DATABASE_DSN = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        elif not self.DATABASE_DSN:
            raise ValueError(
                "DATABASE_DSN is required when POSTGRES_* variables are not fully provided"
            )
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
