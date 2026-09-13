from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from api.v1.oauth import oauth_bearer, oauth_bearer_optional
from core.crypto_settings import CryptoSettings, crypto_settings
from db.dependencies import get_db
from models.database import UserORM
from services.crypto import CryptoService
from services.snippets import SnippetsService
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


async def get_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    crypto_service: Annotated[CryptoService, Depends(get_crypto_service)],
    token: Annotated[str, Depends(oauth_bearer)],
) -> UserORM:
    return await _get_user_by_token(user_service, crypto_service, token)


async def get_current_user_optional(
    user_service: Annotated[UserService, Depends(get_user_service)],
    crypto_service: Annotated[CryptoService, Depends(get_crypto_service)],
    token: Annotated[str | None, Depends(oauth_bearer_optional)],
) -> UserORM | None:
    if token is None:
        return None

    return await _get_user_by_token(user_service, crypto_service, token)


def get_snippets_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SnippetsService:
    return SnippetsService(db=db)


async def _get_user_by_token(
    user_service: UserService,
    crypto_service: CryptoService,
    token: str,
) -> UserORM:
    user_data = await crypto_service.decode_access_token_async(token)

    if user_data is None or "sub" not in user_data or not user_data["sub"]:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )

    user = await user_service.get_by_email(user_data["sub"])

    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )

    return user
