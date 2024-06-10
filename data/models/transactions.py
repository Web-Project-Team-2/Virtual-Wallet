from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Transaction(BaseModel):
    id: Optional[int] = None
    status: Optional[str] = 'pending'
    condition: Optional[str] = 'edited'
    transaction_date: Optional[datetime] = None
    amount: float
    category_name: Optional[str] = 'no category'
    sender_id: Optional[int] = None
    receiver_id: int
    cards_id: Optional[int] = None

    @classmethod
    def from_query_result(cls, id, status, condition, transaction_date, amount, 
                          category_name, sender_id, receiver_id, cards_id):
        return cls(
            id=id,
            status=status,
            condition=condition,
            transaction_date=transaction_date,
            amount=amount,
            category_name=category_name,
            sender_id=sender_id,
            receiver_id=receiver_id,
            cards_id=cards_id
        )