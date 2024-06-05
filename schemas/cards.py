from pydantic import BaseModel


class CardCreate(BaseModel):
    card_number: str  # changed from int to str
    cvv: str          # changed from int to str
    card_holder: str
    expiration_date: str

    def to_dict(self):
        return {
            "card_number": self.card_number,
            "cvv": self.cvv,
            "card_holder": self.card_holder,
            "expiration_date": self.expiration_date,
        }


class ViewCard(BaseModel):
    card_number: int
    cvv: int
    card_holder: str

