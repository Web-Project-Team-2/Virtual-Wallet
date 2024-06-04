from pydantic import BaseModel
from datetime import datetime


class RecurringTransaction(BaseModel):
    id: int | None = None
    recurring_transaction_date: datetime | None = None
    next_payment: datetime | None = None
    status: str = 'pending' 
    condition: str = 'edited'
    amount: float
    sender_id: int | None = None
    receiver_id: int
    categories_id: int | None = None

    @classmethod
    def from_query_result(cls, id, recurring_transaction_date, next_payment, status,
                          condition, amount, sender_id, receiver_id, categories_id,):
        return cls(
            id=id,
            recurring_transaction_date=recurring_transaction_date,
            next_payment=next_payment,
            status=status,
            condition=condition,
            amount=amount,
            sender_id=sender_id,
            receiver_id=receiver_id,
            categories_id=categories_id,
        )