from pydantic import BaseModel, constr

pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}|:"<>?[\];\',.\/\\]).{8,}$'


class Role:
    ADMIN = 'admin'
    STANDARD = 'standard'


class User(BaseModel):
    id: int | None = None
    username: constr(min_length=2, max_length=20)
    password: constr(pattern=pattern)
    email: str
    phone_number: constr(strip_whitespace=True, min_length=10, max_length=10)
    role: str = Role.STANDARD

    @classmethod
    def from_query_result(cls, id, username, password, email, phone_number, role):
        return cls(
            id=id,
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
            role=role
        )


class LoginData(BaseModel):
    username: str
    password: str
    email: str | None = None
