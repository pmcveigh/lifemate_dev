import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

MIN_SECRET_KEY_LENGTH = 32


def _load_environment() -> None:
    env_file = ".env.dev" if os.getenv("ENVIRONMENT") != "production" else ".env.prod"
    if os.path.exists(env_file):
        load_dotenv(env_file)


class Settings(BaseModel):
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if not value:
            raise ValueError("JWT_SECRET_KEY must be set")
        if len(value) < MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters long"
            )
        return value


@lru_cache()
def get_settings() -> Settings:
    _load_environment()
    return Settings()
