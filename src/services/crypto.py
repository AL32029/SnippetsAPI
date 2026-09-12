import datetime
from datetime import timedelta

import jwt
from passlib.context import CryptContext

from core.crypto_settings import crypto_settings


class CryptoService:
    _algorithm = crypto_settings.ALGORITHM
    _jwt_secret_key = crypto_settings.JWT_SECRET_KEY
    _bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self._bcrypt_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self._bcrypt_context.verify(password, hashed_password)

    def create_access_token(
        self,
        data: dict,
        expired_delta: timedelta = timedelta(minutes=15),
    ):
        to_encode = data.copy()

        expire_to = int(
            (datetime.datetime.now(datetime.UTC) + expired_delta).timestamp()
        )
        to_encode.update({"exp": expire_to})

        return jwt.encode(to_encode, self._jwt_secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict | None:
        data = jwt.decode(token, self._jwt_secret_key, algorithms=self._algorithm)

        if (
            not data
            or "exp" not in data
            or not isinstance(data["exp"], int)
            or data["exp"] < datetime.datetime.now(datetime.UTC).timestamp()
        ):
            return None

        return data
