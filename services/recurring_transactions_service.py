from data.models.recurring_transactions import RecurrringTransaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query
from schemas.transactions import TransactionViewAll
from common.responses import Unauthorized, NotFound, BadRequest


def view_all_recurring_transactions():
    pass


def sort_transactions():
     pass


def view_recurring_transaction_by_id():
     pass 


def create_recurring_transactions():
     pass


def recurring_transaction_id_exists():
     pass


def approve_recurring_transaction():
     pass


def get_user_by_id(user_id: int):
    user_data = read_query('''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance
                              FROM users
                              WHERE id = ?''', (user_id,))
    
    user = next((User.from_query_result(*row) for row in user_data), None)

    return user


def get_category_by_id(category_id: int):
    category_data = read_query(
        'SELECT id, name FROM categories WHERE id = ?',
        (category_id,))

    category = next((Category.from_query_result(*row) for row in category_data), None)

    return category


def get_card_by_id(card_id: int):
    card_data = read_query('''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                              FROM cards
                              WHERE id = ?''', (card_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    return card


def user_id_exists(user_id: int):
    return any(read_query(
        '''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance 
               FROM users 
               WHERE id = ?''',
        (user_id,)))
