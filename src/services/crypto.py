import datetime
from datetime import timedelta

import bcrypt
import jwt
from starlette.concurrency import run_in_threadpool

from core.crypto_settings import CryptoSettings


class CryptoService:
    def __init__(self, settings: CryptoSettings):
        self._algorithm = settings.ALGORITHM
        self._jwt_secret_key = settings.JWT_SECRET_KEY

    async def hash_password_async(self, password: str) -> str:
        return await run_in_threadpool(self.hash_password, password)

    async def verify_password_async(self, password: str, hashed: str) -> bool:
        return await run_in_threadpool(self.verify_password, password, hashed)

    async def create_access_token_async(
        self,
        data: dict,
        expired_delta: timedelta = timedelta(minutes=15),
    ) -> str:
        return await run_in_threadpool(self.create_access_token, data, expired_delta)

    async def decode_access_token_async(self, token: str) -> dict | None:
        return await run_in_threadpool(self.decode_access_token, token)

    def create_access_token(
        self,
        data: dict,
        expired_delta: timedelta = timedelta(minutes=15),
    ) -> str:
        to_encode = data.copy()

        expire_to = int(
            (datetime.datetime.now(datetime.UTC) + expired_delta).timestamp()
        )
        to_encode.update({"exp": expire_to})

        return jwt.encode(to_encode, self._jwt_secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict | None:
        try:
            data = jwt.decode(token, self._jwt_secret_key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        return data

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except ValueError:
            return False
