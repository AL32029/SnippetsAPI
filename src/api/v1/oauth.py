from fastapi.security import OAuth2PasswordBearer

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
