from pydantic import BaseModel


class Card(BaseModel):
    card_number: int
    cvv: int
    card_holder: str
    expiration_date: int
    card_status: str
    user_id: int

    @classmethod
    def from_query_result(cls, card_number, cvv, card_holder, expiration_date,
                          card_status, user_id):
        return cls(
            card_number=card_number,
            cvv=cvv,
            card_holder=card_holder,
            expiration_date=expiration_date,
            card_status=card_status,
            user_id=user_id
        )


