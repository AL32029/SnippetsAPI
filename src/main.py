from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import auth_router, snippets_router
from db.engine import engine

# TODO: Добавить в src.services сервис для сниппетов
# TODO: Реализовать тесты для системы на базе pytest (не менее 70% покрытия кода тестами)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(snippets_router)
