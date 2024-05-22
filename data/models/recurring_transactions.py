from pydantic import BaseModel
from datetime import datetime


class RecurrringTransaction(BaseModel):
    id: int | None = None
    next_payment: datetime 
    users_id: int
    categories_id: int | None = None

    @classmethod
    def from_query_result(cls, id, next_payment, users_id, categories_id,):
        return cls(
            id=id,
            next_payment=next_payment,
            users_id=users_id,
            categories_id=categories_id,
        )