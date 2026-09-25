import json
import os
from typing import Any, List

from pydantic import PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
ENV_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, extra="ignore", case_sensitive=True
    )

    DEBUG: bool = False

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = True

    CORS_ORIGINS: Any = []

    AVERAGE_SPEED_KMH: float = 60.0

    # S3 / MinIO Settings
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=self.DB_NAME,
            )
        )


settings = Settings()
