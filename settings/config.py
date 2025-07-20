from datetime import timedelta, timezone
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


moscow_tz = timezone(timedelta(hours=3))


class Settings(BaseSettings):
    ROOT_PATH: Path = Path(__file__).parent.parent
    
    # database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str

    REDIS_DB: int
    REDIS_HOST: str
    REDIS_PORT: int

    ADMIN_PASSWORD: str
    SECRET_KEY: str

    HOST: str
    PORT: int

    model_config = SettingsConfigDict(
        env_file=ROOT_PATH / ".env", env_file_encoding="utf-8"
    )

    def get_redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_db_url(self, test=False):
        if test:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/testing_database"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
