from fastapi.security import OAuth2PasswordBearer

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth_bearer_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False,
)
