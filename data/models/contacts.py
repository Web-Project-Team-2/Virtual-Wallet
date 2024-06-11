from pydantic import BaseModel
from typing import Optional


class Contact(BaseModel):
    users_id: Optional[int] = None
    contact_user_id: int

    @classmethod
    def from_query_result(cls, users_id, contact_user_id):
        return cls(users_id=users_id,
                   contact_user_id=contact_user_id)