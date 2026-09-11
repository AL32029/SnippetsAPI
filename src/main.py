from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
