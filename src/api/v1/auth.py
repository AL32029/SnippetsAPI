from typing import Annotated

import sqlalchemy.exc
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from schemas.user import UserLoginSchema, UserProfileSchema, UserRegisterSchema
from services.crypto import CryptoService
from services.dependencies import get_crypto_service, get_user_service
from services.user import UserService

auth_router = APIRouter(prefix="/auth", tags=["User Profile"])


@auth_router.post("/register")
async def register_user_endpoint(
    register_data: UserRegisterSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        await user_service.save(
            name=register_data.name,
            email=register_data.email,
            password=register_data.password,
        )

        return JSONResponse(
            status_code=HTTP_201_CREATED,
            content={"response": "The user was successfully registered"},
        )
    except sqlalchemy.exc.IntegrityError as err:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="The specified email address is already taken",
        ) from err


@auth_router.post("/login", response_model=UserProfileSchema)
async def login_user_endpoint(
    login_data: UserLoginSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileSchema:
    user = await user_service.login(
        email=login_data.email,
        password=login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )

    return UserProfileSchema(
        id=user.id,
        email=user.email,
        name=user.name,
    )


@auth_router.post("/token")
async def token_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    crypto_service: Annotated[CryptoService, Depends(get_crypto_service)],
) -> dict[str, str]:
    user = await user_service.login(
        email=form_data.username, password=form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )
    access_token = await crypto_service.create_access_token_async(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}
