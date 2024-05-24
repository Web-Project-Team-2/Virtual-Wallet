import datetime
from typing import Optional
from mariadb import IntegrityError
import security.password_hashing
from common.helper_functions import convert_to_datetime
from data.database_queries import insert_query, read_query, delete_query, update_query
from data.models.cards import Card
from data.models.user import User
from schemas.cards import ViewCard
from schemas.transactions import TransactionView, TransactionFilters
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


def create_contact(user_id: int, contact_user_id: int) -> Optional[dict]:
    try:
        insert_query(
            'INSERT INTO contacts (users_id, contact_user_id) VALUES (%s, %s)',
            (user_id, contact_user_id)
        )
        contact_username = read_query(
            'SELECT username FROM users WHERE id = %s',
            (contact_user_id,)
        )
        return {"contact_user_id": contact_user_id, "contact_username": contact_username[0][0]}
    except IntegrityError:
        return None


def delete_contact(user_id: int, contact_user_id: int) -> bool:
    existing_contact = read_query(
        'SELECT * FROM contacts WHERE users_id = %s AND contact_user_id = %s',
        (user_id, contact_user_id)
    )
    if not existing_contact:
        return False  # No such contact exists

    try:
        delete_query(
            'DELETE FROM contacts WHERE users_id = %s AND contact_user_id = %s',
            (user_id, contact_user_id)
        )
        return True
    except IntegrityError:
        return False


def get_all_contacts(user_id: int) -> Optional[list]:
    try:
        contacts = read_query(
            'SELECT contact_user_id, (SELECT username FROM users WHERE id = contact_user_id) AS contact_username FROM contacts WHERE users_id = %s',
            (user_id,)
        )
        return [{"contact_user_id": contact[0], "contact_username": contact[1]} for contact in contacts]
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return None


def update_profile(user_id: int, email: str, password: str, phone_number: str):
    update_result = update_query(
        'UPDATE users SET email = %s, password = %s, phone_number = %s WHERE id = %s',
        (email, password, phone_number, user_id))

    if update_result:
        result = "User information updated successfully"
    else:
        result = "Failed to update user information"

    return result


def deposit_money(user_id: int, balance: int):
    if balance < 25:
        return f"Minimum deposit is $25."

    get_user_balance = read_query('SELECT balance from users WHERE id=?', (user_id,))
    new_balance = balance + get_user_balance[0][0]

    update_result = update_query(
        'UPDATE users SET balance = %s WHERE id = %s',
        (new_balance, user_id))

    if update_result:
        return f"You have successfully deposited ${balance} into your virtual wallet."
    else:
        return f"Unable to deposit ${balance} into your account."


def withdraw_money(user_id: int, withdraw: int):
    get_user_balance = read_query('SELECT balance from users WHERE id=?', (user_id,))

    if withdraw > get_user_balance[0][0]:
        return "Unable to withdraw. You don't have enough cash in your virtual wallet."
    new_balance = get_user_balance[0][0] - withdraw

    update_result = update_query(
        'UPDATE users SET balance = %s WHERE id = %s',
        (new_balance, user_id))

    if update_result:
        return f"You have successfully withdraw ${withdraw} from your virtual wallet."
    else:
        return f"Unable to withdraw ${withdraw} into your account."













