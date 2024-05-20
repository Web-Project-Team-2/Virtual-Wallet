from datetime import datetime
from pydantic import BaseModel, constr, EmailStr


class User(BaseModel):
    id: int | None
    email: EmailStr
    username: str
    password: constr(min_length=8)
    phone_number: str
    is_admin: bool = False
    create_at: datetime | None
    status: str = 'pending'
    balance: float = 0.0

    @classmethod
    def from_query_result(cls, id, email, username, password, phone_number, is_admin, create_at, status, balance):
        return cls(
            id=id,
            email=email,
            username=username,
            password=password,
            phone_number=phone_number,
            is_admin=bool(is_admin),
            create_at=create_at,
            status=status,
            balance=balance
        )
