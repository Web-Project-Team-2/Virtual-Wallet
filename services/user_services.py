from typing import Optional
from mariadb import IntegrityError
import security.password_hashing
from data.database_queries import insert_query, read_query
from data.models.user import User


def create(username: str, password: str, email: str, phone: str) -> Optional[User]:
    try:
        generated_id = insert_query(
            'INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)',
            (username,password, email, phone)
        )
        if generated_id == -1:
            return None
        data = read_query(
            'SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance FROM users WHERE id = %s',
            (generated_id,)
        )
        return next((User.from_query_result(*row) for row in data), None)
    except IntegrityError:
        return None


def find_by_email(email: str) -> Optional[User]:
    data = read_query(
        'SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance FROM users WHERE email = %s',
        (email,)
    )
    return next((User.from_query_result(*row) for row in data), None)


def try_login(email: str, password: str) -> Optional[User]:
    user = find_by_email(email)
    if user and security.password_hashing.verify_password(password, user.password):
        return user
    return None
