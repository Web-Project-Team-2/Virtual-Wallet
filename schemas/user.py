from datetime import datetime
from typing import Optional

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
