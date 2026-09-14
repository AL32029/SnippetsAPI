import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import auth_router, snippets_router
from core.logging_settings import logging_settings
from db.engine import engine

logging.config.dictConfig(logging_settings.model_dump(mode="json"))
logger = logging.getLogger(__name__)

# [MISC][INPROGRESS] Добавить в src.services сервис для сниппетов
# TODO: Реализовать тесты для системы на базе pytest (не менее 70% покрытия кода тестами)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    logger.debug("Launching the server API")

    logger.info("The API server was successfully launched")
    yield
    logger.debug("Stopping the server API")

    logger.debug("Disconnection from the database")
    await engine.dispose()
    logger.debug("The database connection has been lost")

    logger.info("The API server was successfully stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(snippets_router)
