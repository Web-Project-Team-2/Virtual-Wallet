import datetime
from data.database_queries import insert_query, delete_query, read_query
from common.helper_functions import convert_to_datetime
from data.models.cards import Card

async def create(card_number: int, card_holder: str, cvv: int, expiration_date: datetime, user_id):
    exp_date = convert_to_datetime(expiration_date)
    await insert_query('''
    INSERT INTO cards (card_number, card_holder, cvv, expiration_date, user_id) VALUES (%s, %s, %s, %s, %s)''',
                 (card_number, card_holder, cvv, exp_date, user_id))

async def delete(card_id: int, user_id: int):
    try:
        success = await delete_query('DELETE FROM cards WHERE id = %s AND user_id = %s', (card_id, user_id))
        return success
    except Exception as e:
        return f"Error deleting debit card: {e}"

async def get_card_by_id(card_id: int):
    card_data = await read_query('''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                              FROM cards
                              WHERE id = %s''', (card_id,))
    return Card.from_query_result(*card_data[0]) if card_data else None
