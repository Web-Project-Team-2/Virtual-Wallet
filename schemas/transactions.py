from pydantic import BaseModel, constr
from datetime import datetime, timedelta


class TransactionUserContact(BaseModel):
    status: str 
    amount: float
    sender_id: int 
    receiver_id: int


class TransactionCategory(BaseModel):
    status: str 
    amount: float
    next_payment: datetime = datetime.now() + timedelta(weeks=4)
    categories_id: int 
    sender_id: int
    receiver_id: int