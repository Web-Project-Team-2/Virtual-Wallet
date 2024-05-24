from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TransactionViewAll(BaseModel):
    status: str 
    transaction_date: str
    amount: float
    sender: str
    receiver: str
    direction: str

    @classmethod
    def transactions_view(cls, transaction, sender, receiver, direction):
        return cls(
            status=transaction.status,
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            sender=sender.username,
            receiver=receiver.username,
            direction=direction
        )


class TransactionView(BaseModel):
    status: str 
    transaction_date: str
    amount: float
    sender: str 
    receiver: str
    direction: str
    card_holder: str
    card_number: int

    @classmethod
    def transaction_view(cls, transaction, sender, receiver, direction, card_holder, card_number):
       
        return cls(
            status=transaction.status,
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            sender=sender.username,
            receiver=receiver.username,
            direction=direction,
            card_holder=card_holder.card_holder,
            card_number=card_number.card_number
        )


class TransactionFilters(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sender_id: Optional[int] = None
    recipient_id: Optional[int] = None
    direction: Optional[str] = None
    limit: int = 10
    offset: int = 0
    sort_by: str = 'transaction_date'
    sort_order: str = 'asc'