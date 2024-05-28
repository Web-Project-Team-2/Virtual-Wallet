from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=20)
    password: constr(min_length=6)
    phone_number: constr(min_length=10, max_length=10)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    email: EmailStr
    username: str
    phone_number: str


class UserInfo(BaseModel):
    username: Optional[str]
    email: str
    balance: int
    phone_number: int


class UserInfoUpdate(BaseModel):
    email: str
    password: str
    phone_number: str


class AdminUserInfo(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    is_admin: bool
    create_at: datetime
    status: str
    balance: float

    @classmethod
    def from_query_result(cls, id, username, email, phone_number, is_admin, create_at, status, balance):
        return cls(
            id=id,
            username=username,
            email=email,
            phone_number=phone_number,
            is_admin=bool(is_admin),
            create_at=create_at,
            status=status,
            balance=balance
        )
