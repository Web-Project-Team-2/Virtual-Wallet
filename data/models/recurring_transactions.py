from pydantic import BaseModel
from datetime import datetime


class RecurrringTransaction(BaseModel):
    id: int | None = None
    recurring_transaction_date: datetime | None = None
    next_payment: datetime | None = None
    status: str = 'pending' 
    condition: str = 'edited'
    amount: float
    users_id: int | None = None
    categories_id: int | None = None

    @classmethod
    def from_query_result(cls, id, recurring_transaction_date, next_payment,
                          status, condition, amount, users_id, categories_id,):
        return cls(
            id=id,
            recurring_transaction_date=recurring_transaction_date,
            next_payment=next_payment,
            status=status,
            condition=condition,
            amount=amount,
            users_id=users_id,
            categories_id=categories_id,
        )