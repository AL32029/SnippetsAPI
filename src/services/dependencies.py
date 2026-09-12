from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.crypto_settings import CryptoSettings, crypto_settings
from db.dependencies import get_db
from services.crypto import CryptoService
from services.user import UserService


@lru_cache
def get_crypto_settings() -> CryptoSettings:
    return crypto_settings


def get_crypto_service(
    settings: Annotated[CryptoSettings, Depends(get_crypto_settings)],
) -> CryptoService:
    return CryptoService(settings=settings)


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    crypto: Annotated[CryptoService, Depends(get_crypto_service)],
) -> UserService:
    return UserService(db=db, crypto=crypto)
