from pydantic import BaseModel
from typing import Optional

class ContactCreate(BaseModel):
    contact_user_id: int


class ContactsViewAll(BaseModel):
    username: str

    @classmethod
    def contacts_view(cls, username):
        return cls(username=username)


class ContactView(BaseModel):
    username: str
    email: str
    phone_number: str

    @classmethod
    def contacts_view(cls, username, email, phone_number):
        return cls(username=username,
                   email=email,
                   phone_number=phone_number)
