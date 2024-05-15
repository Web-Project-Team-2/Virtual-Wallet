from pydantic import BaseModel, constr, conint, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int | None
    username: constr()
    password: str
    email: str
    phone_number: str


    @classmethod
    def from_query_result(cls, id, username, password, email):
        return cls(
            id=id,
            username=username,
            password=password,
            email=email)

