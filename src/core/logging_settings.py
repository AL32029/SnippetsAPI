import os

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(json_file=os.getenv("LOGGING_SETTINGS_PATH"))

    version: int = 1
    disable_existing_loggers: bool = Field(False)
    formatters: dict = Field(
        {
            "default": {
                "format": "[%(asctime)s | %(levelname)s] %(name)s: %(message)s",
            }
        }
    )
    handlers: dict = Field(
        {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        }
    )
    loggers: dict = Field({})
    root: dict = Field(
        {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        }
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


logging_settings = LoggingSettings()
