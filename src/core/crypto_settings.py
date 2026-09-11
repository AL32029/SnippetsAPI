from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CryptoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CRYPTO_")

    SECRET_KEY: str = Field(min_length=1)
