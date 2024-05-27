from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class TransactionViewAll(BaseModel):
    transaction_date: str
    amount: float
    sender: str
    receiver: str
    direction: str

    @classmethod
    def transactions_view(cls, transaction, sender, receiver, direction):
        return cls(
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            sender=sender.username,
            receiver=receiver.username,
            direction=direction
        )

class TransactionView(BaseModel):
    status: str 
    condition: str 
    transaction_date: str
    amount: float
    category_name: str
    sender: str 
    receiver: str
    direction: str

    @classmethod
    def transaction_view(cls, transaction, sender, receiver, direction):
       
        return cls(
            status=transaction.status,
            condition=transaction.condition,
            transaction_date=transaction.transaction_date.strftime('%Y/%m/%d %H:%M'),
            amount=transaction.amount,
            category_name=transaction.category_name,
            sender=sender.username,
            receiver=receiver.username,
            direction=direction
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