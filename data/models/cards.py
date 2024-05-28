from pydantic import BaseModel
from datetime import date


class Card(BaseModel):
    id: int | None = None
    card_number: int
    cvv: int
    card_holder: str
    expiration_date: date
    card_status: str
    user_id: int
    balance: float | None = None

    @classmethod
    def from_query_result(cls, id, card_number, cvv, card_holder, expiration_date,
                          card_status, user_id, balance):
        return cls(
            id=id,
            card_number=card_number,
            cvv=cvv,
            card_holder=card_holder,
            expiration_date=expiration_date,
            card_status=card_status,
            user_id=user_id,
            balance=balance
        )

    def to_dict(self):
        return {
            "card_number": self.card_number,
            "cvv": self.cvv,
            "card_holder": self.card_holder,
            "expiration_date": self.expiration_date,
            "card_status": self.card_status,
            "user_id": self.user_id
        }
