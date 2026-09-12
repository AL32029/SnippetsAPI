import datetime
from datetime import timedelta

import bcrypt
import jwt

from core.crypto_settings import CryptoSettings


class CryptoService:
    def __init__(self, settings: CryptoSettings):
        self._algorithm = settings.ALGORITHM
        self._jwt_secret_key = settings.JWT_SECRET_KEY

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def create_access_token(
        self,
        data: dict,
        expired_delta: timedelta = timedelta(minutes=15),
    ):
        to_encode = data.copy()

        expire_to = (datetime.datetime.now(datetime.UTC) + expired_delta).timestamp()
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
