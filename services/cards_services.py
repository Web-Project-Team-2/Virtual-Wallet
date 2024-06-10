import datetime
from data.database_queries import insert_query, delete_query, read_query
from common.helper_functions import convert_to_datetime
from data.models.cards import Card

async def create(card_number: str, card_holder: str, cvv: str, expiration_date: str, user_id: int):
    exp_date = convert_to_datetime(expiration_date)
    await insert_query('''
    INSERT INTO cards (card_number, card_holder, cvv, expiration_date, user_id) VALUES ($1, $2, $3, $4, $5)''',
                 (card_number, card_holder, cvv, exp_date, user_id))

async def delete(card_id: int, user_id: int) -> bool:
    try:
        success = await delete_query('DELETE FROM cards WHERE id = $1 AND user_id = $2', (card_id, user_id))
        return success
    except Exception as e:
        raise Exception(f"Error deleting card: {e}")

async def get_card_by_id(card_id: int):
    card_data = await read_query('''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                              FROM cards
                              WHERE id = $1''', (card_id,))
    return Card.from_query_result(*card_data[0]) if card_data else None


async def get_card_info_by_id(card_id: int) -> Card:
    '''
    This function retrieves a card from the database based on its ID.\n
    Parameters:\n
    - card_id : int\n
        - The ID of the card to retrieve.
    '''
    card_data = await read_query(sql='''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                                        FROM cards
                                        WHERE id = $1''',
                                 sql_params=(card_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    return card


async def get_card_by_user_id(cards_user_id: int) -> int:
    '''
    This function retrieves a card ID from the database based on the user's ID.\n
    Parameters:\n
    - cards_user_id : int\n
        - The ID of the user whose card ID is being retrieved.
    '''

    card_data = await read_query(sql='''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                                        FROM cards
                                        WHERE user_id = $1''',
                           sql_params=(cards_user_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    card_id = card.id

    return card_id