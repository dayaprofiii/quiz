from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Quizleet API'
    environment: str = Field(default='development')
    database_url: str = Field(
        default='postgresql+psycopg://quizleet:quizleet@127.0.0.1:5433/quizleet',
        validation_alias='DATABASE_URL',
    )
    allowed_origins: list[str] = ['http://127.0.0.1:3000', 'http://localhost:3000']
    auto_create_db: bool = Field(default=True, validation_alias='AUTO_CREATE_DB')
    seed_demo_data: bool = Field(default=True, validation_alias='SEED_DEMO_DATA')


@lru_cache
def get_settings() -> Settings:
    return Settings()
