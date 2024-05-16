
from mariadb import IntegrityError

import security.password_hashing
from data.database_queries import insert_query, read_query
from data.models.user import User


def create(username: str, password: str, email: str, phone: int) -> User | None:
    try:
        generated_id = insert_query('insert into user(username, password, email, phone) values(?, ?, ?, ?)',
                                    (username, password,
                                     email, phone))
        return User(id=generated_id, username=username, password="", phone=phone)

    except IntegrityError:
        return None


def find_by_email(email: str) -> User | None:
    data = read_query('SELECT id, email, username, password FROM user WHERE email = ?', (email,))
    return next((User.from_query_result(*row) for row in data), None)


def try_login(email: str, password: str) -> User | None:
    user = find_by_email(email)

    hashed_pass = security.password_hashing.get_password_hash(password)
    return user if user and user.password == hashed_pass else None
