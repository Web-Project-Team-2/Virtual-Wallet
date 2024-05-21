from typing import Optional
from mariadb import IntegrityError
import security.password_hashing
from common.helper_functions import convert_to_datetime
from data.database_queries import insert_query, read_query
from data.models.cards import Card
from data.models.user import User
from schemas.cards import ViewCard
from schemas.transactions import ViewTransactions
from schemas.user import UserInfo


def create(username: str, password: str, email: str, phone: str) -> Optional[User]:
    try:
        generated_id = insert_query(
            'INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)',
            (username, password, email, phone)
        )
        if not generated_id:
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


def view(user_id: int):
    # Fetch user card information
    card_info = read_query('SELECT card_number, balance, card_holder from cards WHERE user_id = %s', (user_id,))

    # Generate card objects
    cards = [
        {"card_number": card_number, "balance": balance, "card_holder": card_holder}
        for card_number, balance, card_holder in card_info
    ]

    # Fetch user transaction information
    transactions_data = read_query(
        'SELECT status, transaction_date, amount, cards_id, receiver_id from transactions WHERE sender_id = %s',
        (user_id,))

    # Generate transaction objects
    transactions = [
        {"status": status, "transaction_date": transaction_date, "amount": amount, "card_id": card_id,
         "receiver_id": receiver_id}
        for status, transaction_date, amount, card_id, receiver_id in transactions_data
    ]

    if not transactions:
        transactions = "No transactions"

    # Check if any cards exist for the user
    if card_info:
        display_info = {
            "cards": cards,
            "transactions": transactions
        }
    else:
        display_info = {
            "message": "No cards found for the user",
            "transactions": transactions
        }

    return display_info


def view_profile(user_id: int):
    user_info = read_query('SELECT username, email, balance, phone_number from users WHERE id = %s', (user_id,))
    result = (UserInfo(username=username, email=email, balance=balance, phone_number=phone_number) for
              username, email, balance, phone_number in user_info)

    if not user_info:
        result = "No user information available"

    return result


def user_id_exists(user_id: int):
    return any(read_query(
        '''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance 
               FROM users 
               WHERE id = ?''',
        (user_id,)))
