from pydantic import BaseModel, EmailStr, Field


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=64)


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserProfileSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
