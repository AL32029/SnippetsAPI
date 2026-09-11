from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    HOST: str = Field(min_length=1)
    PORT: int

    USER: str = Field(min_length=1)
    PASSWORD: str = Field(min_length=1)

    BASE: str = Field(min_length=1)

    @property
    def database_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            host=self.HOST,
            port=self.PORT,
            username=self.USER,
            password=self.PASSWORD,
            path=self.BASE,
        )


database_settings = DatabaseSettings()
