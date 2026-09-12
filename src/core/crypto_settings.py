from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CryptoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CRYPTO_")

    ALGORITHM: str = Field("HS256")

    JWT_SECRET_KEY: str = Field(min_length=32)


crypto_settings = CryptoSettings()
