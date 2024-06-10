from data.models.recurring_transactions import RecurringTransaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query
from common.responses import BadRequest, NotFound
from datetime import datetime


sql_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, condition, amount, sender_id, receiver_id, categories_id
                                FROM recurring_transactions'''

sender_id_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, condition, amount, sender_id, receiver_id, categories_id
                                      FROM recurring_transactions
                                      WHERE sender_id = $1'''

id_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, condition, amount, sender_id, receiver_id, categories_id
                                      FROM recurring_transactions
                                      WHERE id = $1'''

values_recurring_transactions = '''INSERT INTO recurring_transactions (recurring_transaction_date, next_payment, status, condition, amount, sender_id, receiver_id, categories_id) 
                                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)'''


async def view_all_recurring_transactions(current_user: int,
                                          recurring_transaction_date: str | None = None,
                                          categories_id: int | None = None):
    '''
    This function returns a list of all the recurring transactions for the specified user.\n
    Parameters:\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.\n
    - transaction_date: str | None\n
        - Filter transactions by a specific date.\n
    - categories_id: int | None\n
        Filter recurring transactions by category ID.
    '''

    loc_sql_recurring_transactions = sql_recurring_transactions

    if recurring_transaction_date or categories_id:
        filter_by = []
        sql_parameters = []
        if recurring_transaction_date:
            recurring_transaction_date = datetime.strptime(recurring_transaction_date, '%Y-%m-%d').date()
            if not recurring_transaction_date:
                return BadRequest(content=f'Incorrect date format, should be YYYY-MM-DD.')
            filter_by.append(f'recurring_transaction_date = $1')
            sql_parameters.append(recurring_transaction_date)
        if categories_id:
            filter_by.append(f'categories_id = %2')
            sql_parameters.append(categories_id)

        if filter_by:
            loc_sql_recurring_transactions += ' WHERE ' + ' AND '.join(filter_by)

        sql_parameters = tuple(sql_parameters)
        rows = await read_query(sql=loc_sql_recurring_transactions ,
                                sql_params=sql_parameters)
    
        if rows is not None:
            return [RecurringTransaction.from_query_result(*row) for row in rows]
        else:
            return NotFound(content=f'The required transactions you are looking for are not available.')
     
    else:
        recurring_transactions = await read_query(sql=sender_id_recurring_transactions,
                                                  sql_params=(current_user,))

        recurring_transactions_all = []
        for row in recurring_transactions:
            recurring_transaction = RecurringTransaction.from_query_result(*row)
            if recurring_transaction not in recurring_transactions_all:
                recurring_transactions_all.append(recurring_transaction)

        return recurring_transactions_all


def sort_recurring_transactions(recurring_transactions: list[RecurringTransaction], *,
                                attribute='recurring_transaction_date',
                                reverse=False):
    '''
    This function sorts a list of recurring transactions based on a specified attribute.\n
    Parameters:\n
    - recurring_transactions: list[RecurringTransaction]\n
        - A list of RecurringTransaction objects to be sorted.
    - attribute: str\n
        - The attribute to sort the transactions by. Default is 'recurring_transaction_date'.\n
    - reverse: bool\n
        - Whether to sort in reverse order. Default is False (ascending order).
    '''

    if attribute == 'recurring_transaction_date':
        def sort_fn(t: RecurringTransaction): return t.recurring_transaction_date
    elif attribute == 'amount':
        def sort_fn(t: RecurringTransaction): return t.amount
    else:
        return BadRequest(content=f'Unsupported sort attribute: {attribute}.')
     
    return sorted(recurring_transactions, key=sort_fn, reverse=reverse)


async def view_recurring_transaction_by_id(recurring_transaction_id: int,
                                           current_user: int):
    '''
    This function returns a more detailed information about a user's transactions.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the transaction to retrieve details for.\n
    - current_user : int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''

    recurring_transactions = await read_query(sql=sender_id_recurring_transactions,
                                              sql_params=(current_user,))

    if not recurring_transactions:
        return None
    
    recurring_transaction_by_id = await read_query(sql=id_recurring_transactions,
                                                   sql_params=(recurring_transaction_id,))
     
    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transaction_by_id), None)

    return recurring_transaction 


async def create_recurring_transaction(recurring_transaction: RecurringTransaction):
    '''
    This function makes a recurring transaction to another user and category.\n
    Parameters:\n
    - recurring_transaction : RecurringTransaction\n
        - The recurring transaction's details to be added to the user's recurring transactions.
    '''

    generated_id = await insert_query(sql=values_recurring_transactions,
                                      sql_params=(recurring_transaction.recurring_transaction_date,
                                                  recurring_transaction.next_payment,
                                                  recurring_transaction.status,
                                                  recurring_transaction.condition,
                                                  recurring_transaction.amount,
                                                  recurring_transaction.sender_id,
                                                  recurring_transaction.receiver_id,
                                                  recurring_transaction.categories_id))

    recurring_transaction.id = generated_id

    return recurring_transaction


async def preview_edited_recurring_transaction(recurring_transaction_id: int,
                                               new_amount: float,
                                               new_category_name: str,
                                               new_receiver_id: int):
    '''
    This function previews a recurring transaction if it will be edited.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - recurring_transaction : RecurringTransaction\n
        - The recurring transaction's details to be added to the user's recurring transactions.\n
    - new_amount: float\n
        - The new amount to update the recurring transaction with.\n
    - new_category_name: str\n
        - The new category name to update the recurring transaction with.\n
    - new_receiver_id: int\n
        - The new receiver ID to update the recurring transaction with.
    '''

    recurring_transactions = await read_query(sql=id_recurring_transactions,
                                              sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    if new_amount:
        edited_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET amount = $1 WHERE id = $2',
                                                          sql_params=(new_amount, recurring_transaction_id))
    if new_category_name:
        edited_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET category_name = $1 WHERE id = $2',
                                                          sql_params=(new_category_name, recurring_transaction_id))
    if new_receiver_id:
        edited_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET receiver_id = $1 WHERE id = $2',
                                                          sql_params=(new_receiver_id, recurring_transaction_id))
          
    edited_recurring_transactions = await read_query(sql=id_recurring_transactions,
                                                     sql_params=(recurring_transaction_id,))

    edited_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in edited_recurring_transactions), None)

    return edited_recurring_transaction


async def preview_sent_recurring_transaction(recurring_transaction_id: int,
                                             amount: float,
                                             status: str,
                                             condition_action: str,
                                             current_user: int):
    '''
    This function previews a recurring transaction if it will be sent.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - amount: float\n
        - The amount to be updated in the recurring transaction.\n
    - status: str\n
        - The new status of the recurring transaction.\n
    - condition_action: str\n
        - The new condition of the recurring transaction.\n
    - current_user: int\n
        - The ID of the currently authenticated user.
    '''

    recurring_transactions = await read_query(sql=id_recurring_transactions,
                                              sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    sender_id = recurring_transaction.sender_id
    receiver_id = recurring_transaction.receiver_id
    cards_id = recurring_transaction.cards_id

    sent_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET status = $1, condition = $2 WHERE id = $3',
                                                    sql_params=(status, condition_action, recurring_transaction_id))
     
    if current_user == sender_id and current_user == receiver_id:
        updated_card_balance = await update_query(sql='UPDATE cards SET balance = balance - $1 WHERE id = $2',
                                                  sql_params=(amount, cards_id))
    if current_user == sender_id and current_user != receiver_id:
        updated_user_balance = await update_query(sql='UPDATE users SET balance = balance - $1 WHERE id = $2',
                                                  sql_params=(amount, sender_id))
    if current_user == receiver_id:
        updated_user_balance = await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                                                  sql_params=(amount, receiver_id))

    sent_recurring_transactions = await read_query(sql=id_recurring_transactions,
                                                   sql_params=(recurring_transaction_id,))

    sent_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in sent_recurring_transactions), None)

    return sent_recurring_transaction


async def preview_confirm_recurring_transaction(recurring_transaction_id: int,
                                                amount: float,
                                                status: str,
                                                condition_action: str,
                                                current_user: int):
    '''
    This function previews a recurring transaction if it will be confirmed.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - amount: float\n
        - The amount to be updated in the recurring transaction.\n
    - status: str\n
        - The new status of the recurring transaction.\n
    - condition_action: str\n
        - The new condition of the recurring transaction.\n
    - current_user: int\n
        - The ID of the currently authenticated user.
    '''

    recurring_transactions = await read_query(sql=id_recurring_transactions,
                                              sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    sender_id = recurring_transaction.sender_id
    receiver_id = recurring_transaction.receiver_id

    confirmed_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET status = $1, condition = $2 WHERE id = $3',
                                                         sql_params=(status, condition_action, recurring_transaction_id))

    if current_user != sender_id and current_user == receiver_id:
        updated_user_balance = await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                                                  sql_params=(amount, receiver_id))
          
    confirmed_recurring_transactions = await read_query(sql=id_recurring_transactions,
                                                        sql_params=(recurring_transaction_id,))

    confirmed_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in confirmed_recurring_transactions), None)

    return confirmed_recurring_transaction


async def preview_cancel_recurring_transaction(recurring_transaction_id: int,
                                               status: str,
                                               condition_action: str):
    '''
    This function previews a recurring transaction if it will be cancelled.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - status: str\n
        - The new status of the recurring transaction.\n
    - condition_action: str\n
        - The new condition of the recurring transaction.\n
    '''

    recurring_transactions = await read_query(sql=id_recurring_transactions,
                                              sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    cancelled_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET status = $1, condition = $2 WHERE id = $3',
                                                         sql_params=(status, condition_action, recurring_transaction_id))
     
    cancelled_recurring_transactions = await read_query(sql=id_recurring_transactions,
                                                        sql_params=(recurring_transaction_id,))

    cancelled_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in cancelled_recurring_transactions), None)

    return cancelled_recurring_transaction


async def preview_decline_recurring_transaction(recurring_transaction_id: int,
                                                amount: float,
                                                status: str,
                                                condition_action: str,
                                                current_user: int):
    '''
    This function previews a recurring transaction if it will be declined.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - amount: float
        The amount of the recurring transaction.
    - status: str
        The new status of the recurring transaction.
    - condition_action: str
        The new condition of the recurring transaction.
    - current_user: int
        The ID of the currently authenticated user.
    '''

    recurring_transactions = await read_query(sql=id_recurring_transactions,
                                              sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    declined_amount = amount
    sender = recurring_transaction.sender_id
    receiver = current_user

    updated_user_balance = await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                                              sql_params=(declined_amount, sender))

    declined_recurring_transaction = await update_query(sql='UPDATE recurring_transactions SET status = $1, condition = $2 WHERE id = $3',
                                                        sql_params=(status, condition_action, recurring_transaction_id))
     

    declined_recurring_transactions = await read_query(sql=id_recurring_transactions,
                                                       sql_params=(recurring_transaction_id,))

    declined_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in declined_recurring_transactions), None)

    return declined_recurring_transaction


async def recurring_transaction_id_exists(recurring_transaction_id: int) -> bool:
    '''
    This function checks if a recurring transaction with the specified ID exists in the database.\n
    Parameters:\n
    - recurring_transaction_id: int\n
        - The ID of the recurring transaction to check for existence.
    '''

    return any(await read_query(sql=id_recurring_transactions,
                                         sql_params=(recurring_transaction_id,)))


async def contact_id_exists(current_user: int,
                            reciever_id: int) -> bool:
    '''
    This function checks if a contact exists between the current user and the receiver.\n
    Parameters:\n
    - current_user : int\n
        - The ID of the current authenticated user.\n
    - reciever_id : int\n
        - The ID of the receiver to check the contact against.
    '''

    return any(await read_query(sql='''SELECT users_id, contact_user_id
                                                FROM contacts 
                                                WHERE users_id = $1 AND contact_user_id = $2''',
                                        sql_params=(current_user, reciever_id,)))