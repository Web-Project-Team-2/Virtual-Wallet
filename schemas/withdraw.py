from pydantic import BaseModel


class WithdrawMoney(BaseModel):
    withdraw_money: int