from typing import Optional

from pydantic import BaseModel, constr
from datetime import datetime, timedelta
from data.models.user import User
from data.models.cards import Card


class TransactionViewAll(BaseModel):
    status: str 
    transaction_date: str
    amount: float
    sender_id: int
    receiver_id: int

    @classmethod
    def transactions_view(cls, transaction):
        return cls(
            status=transaction.status,
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            sender_id=transaction.sender_id,
            receiver_id=transaction.receiver_id
        )


class TransactionView(BaseModel):
    status: str 
    transaction_date: str
    amount: float
    sender_id: int 
    receiver_id: int
    cards_id: int

    @classmethod
    def transaction_view(cls, transaction):
       
        return cls(
            status=transaction.status,
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            sender_id=transaction.sender_id,
            receiver_id=transaction.receiver_id,
            cards_id=transaction.cards_id
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