import datetime
from data.database_queries import insert_query
from common.helper_functions import convert_to_datetime


def create(card_number: int, card_holder: str, cvv: int, expiration_date: datetime, user_id):
    exp_date = convert_to_datetime(expiration_date)

    insert_query('''
    INSERT INTO cards (card_number, card_holder, cvv, expiration_date, user_id)     VALUES (?, ?, ?, ?, ?)''',
                 (card_number, card_holder, cvv, exp_date, user_id))
