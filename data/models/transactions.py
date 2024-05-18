from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    id: int | None = None
    status: str = 'pending'
    transaction_date: datetime 
    amount: float
    next_payment: datetime | None = None
    categories_id: int | None = None
    sender_id: int | None = None
    receiver_id: int
    cards_id: int | None = None

    @classmethod
    def from_query_result(cls, id, status, transaction_date, amount, 
                          next_payment, categories_id, sender_id, reciver_id, cards_id):
        return cls(
            id=id,
            status=status,
            transaction_date=transaction_date,
            amount=amount,
            next_payment=next_payment,
            categories_id=categories_id,
            sender_id=sender_id,
            reciver_id=reciver_id,
            cards_id=cards_id
        )