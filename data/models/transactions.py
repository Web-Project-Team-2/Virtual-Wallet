from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    id: int | None = None
    status: str = 'pending'
    condition: str = 'edited'
    transaction_date: datetime | None = None
    amount: float
    sender_id: int | None = None
    receiver_id: int
    cards_id: int | None = None
    categories_id: int | None = None

    @classmethod
    def from_query_result(cls, id, status, condition, transaction_date, amount, 
                          sender_id, receiver_id, cards_id, categories_id):
        return cls(
            id=id,
            status=status,
            condition=condition,
            transaction_date=transaction_date,
            amount=amount,
            sender_id=sender_id,
            receiver_id=receiver_id,
            cards_id=cards_id,
            categories_id=categories_id
        )