from pydantic import BaseModel, constr


class Category(BaseModel):
    id: int | None = None
    name: constr(min_length=1)

    @classmethod
    def from_query_result(cls, id, name):
        return cls(
            id=id,
            name=name
        )
