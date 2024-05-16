from pydantic import BaseModel, constr, validator


class Role:
    ADMIN = 'admin'
    STANDARD = 'standard'


class User(BaseModel):
    id: int | None = None
    username: constr(min_length=2, max_length=20)
    password: str
    email: str
    phone_number: constr(strip_whitespace=True, min_length=10, max_length=10)
    role: str = Role.STANDARD

    @validator('password')
    def password_complexity(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+{}|:"<>?[\];\',./\\' for char in value):
            raise ValueError('Password must contain at least one special character')
        return value


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
