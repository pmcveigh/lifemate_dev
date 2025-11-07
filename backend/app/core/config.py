import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel


def _load_environment() -> None:
    env_file = ".env.dev" if os.getenv("ENVIRONMENT") != "production" else ".env.prod"
    if os.path.exists(env_file):
        load_dotenv(env_file)


class Settings(BaseModel):
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


@lru_cache()
def get_settings() -> Settings:
    _load_environment()
    return Settings()
