from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    typesafe_api_key: SecretStr
    alpha_vantage_api_key: SecretStr
    alpha_vantage_base_url: str = "https://www.alphavantage.co/query"
    request_timeout_seconds: float = 30.0
    typesafe_model: str = "jev-latest"
    evidence_threshold: float = 0.5


@lru_cache
def get_settings() -> Settings:
    return Settings()