from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'Ecommerce Demo API'
    env: str = 'development'
    port: int = 3000

    mongo_uri: str
    mongo_db: str = 'ecommerce'

    access_token_secret: str
    refresh_token_secret: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    reset_token_expire_minutes: int = 30

    request_id_header: str = 'x-request-id'


@lru_cache
def get_settings() -> Settings:
    return Settings()
