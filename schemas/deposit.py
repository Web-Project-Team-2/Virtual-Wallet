from pydantic import BaseModel


class Deposit(BaseModel):
    deposit_money: int
