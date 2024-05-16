from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str