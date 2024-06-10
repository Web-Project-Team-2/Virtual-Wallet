from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RecurringTransaction(BaseModel):
    id: Optional[int] = None
    recurring_transaction_date: Optional[datetime] = None
    next_payment: Optional[datetime] = None
    status: Optional[str] = 'pending'
    condition: Optional[str] = 'edited'
    amount: float
    sender_id: Optional[int] = None
    receiver_id: int
    categories_id: Optional[int] = None

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