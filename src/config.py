import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    DATABASE_DSN: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str
    UPLOAD_DIR: str  = str(BASE_DIR.joinpath("static").joinpath("images"))
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
