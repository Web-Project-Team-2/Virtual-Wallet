from data.models.recurring_transactions import RecurringTransaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query

base_sql_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, `condition`, amount, sender_id, receiver_id, categories_id
                                FROM recurring_transactions'''

sender_id_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, `condition`, amount, sender_id, receiver_id, categories_id
                                      FROM recurring_transactions
                                      WHERE sender_id = ?'''

id_recurring_transactions = '''SELECT id, recurring_transaction_date, next_payment, status, `condition`, amount, sender_id, receiver_id, categories_id
                                      FROM recurring_transactions
                                      WHERE id = ?'''

values_recurring_transactions = '''INSERT INTO recurring_transactions(id, recurring_transaction_date, next_payment, status, `condition`, amount, sender_id, receiver_id, categories_id) 
                                   VALUES(?,?,?,?,?,?,?,?,?)'''


def view_all_recurring_transactions(current_user: int,
                                    recurring_transaction_date: str | None = None,
                                    categories_id: int | None = None):
    '''
    This function returns a list of all the recurring transactions for the specified user.

    Parameters:
    - current_user: int
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        - This parameter is used to ensure that the request is made by an authenticated user.
    - transaction_date: str | None
        - Filter transactions by a specific date.
    - categories_id: int | None
        - Filter transactions by a specific category ID.
    '''
    sql = base_sql_recurring_transactions
    sql_params = []

    if recurring_transaction_date or categories_id:
        filter_by = []
        if recurring_transaction_date:
            filter_by.append('recurring_transaction_date LIKE ?')
            sql_params.append(f'%{recurring_transaction_date}%')
        if categories_id:
            filter_by.append('categories_id = ?')
            sql_params.append(categories_id)

        if filter_by:
            sql += ' WHERE ' + ' AND '.join(filter_by)

        return [RecurringTransaction.from_query_result(*row) for row in
                read_query(sql=sql, sql_params=tuple(sql_params))]

    else:
        recurring_transactions = read_query(sql=sender_id_recurring_transactions,
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
    if attribute == 'recurring_transaction_date':
        def sort_fn(t: RecurringTransaction): return t.recurring_transaction_date
    if attribute == 'amount':
        def sort_fn(t: RecurringTransaction): return t.amount
     
    return sorted(recurring_transactions, key=sort_fn, reverse=reverse)


def view_recurring_transaction_by_id(recurring_transaction_id: int, current_user: int):
    '''
    This function returns a more detailed information about a user's transactions.\n
    Parameters:\n
    - transaction_id : int\n
        - The ID of the transaction to retrieve details for.\n
    - current_user : int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''
    recurring_transactions = read_query(sql=sender_id_recurring_transactions,
                                        sql_params=(current_user,))

    if recurring_transactions:
        recurring_transaction_by_id = read_query(sql=id_recurring_transactions,
                                                 sql_params=(recurring_transaction_id,))
    else:
        return None
     
    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transaction_by_id), None)

    if recurring_transaction is None:
        return None
    else:
        return recurring_transaction 

def create_recurring_transaction(recurring_transaction: RecurringTransaction):
    '''
    This function makes a transaction to another user or category.\n
    Parameters:
    transaction : Transaction
    The transaction details to be added to the user's wallet.
    '''
    generated_id = insert_query(sql=values_recurring_transactions,
                                sql_params=(recurring_transaction.id,
                                            recurring_transaction.recurring_transaction_date,
                                            recurring_transaction.next_payment,
                                            recurring_transaction.status,
                                            recurring_transaction.condition,
                                            recurring_transaction.amount,
                                            recurring_transaction.sender_id,
                                            recurring_transaction.receiver_id,
                                            recurring_transaction.categories_id))

    recurring_transaction.id = generated_id

    return recurring_transaction


def preview_edited_recurring_transaction(recurring_transaction_id: int, new_amount: float, new_category_name: str, new_receiver_id: int):
    recurring_transactions = read_query(sql=id_recurring_transactions,
                                        sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    if new_amount:
        edited_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET amount = ? WHERE id = ?',
                                                    sql_params=(new_amount, recurring_transaction_id))
    if new_category_name:
        edited_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET category_name = ? WHERE id = ?',
                                                    sql_params=(new_category_name, recurring_transaction_id))
    if new_receiver_id:
        edited_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET reveiver_id = ? WHERE id = ?',
                                                    sql_params=(new_receiver_id, recurring_transaction_id))
          
    edited_recurring_transactions = read_query(sql=id_recurring_transactions,
                                               sql_params=(recurring_transaction_id,))

    edited_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in edited_recurring_transactions), None)

    return edited_recurring_transaction


def preview_send_recurring_transaction(recurring_transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
    recurring_transactions = read_query(sql=id_recurring_transactions,
                                        sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    sender_id = recurring_transaction.sender_id
    receiver_id = recurring_transaction.receiver_id
    cards_id = recurring_transaction.cards_id

    sent_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET status = ?, `condition` = ? WHERE id = ?',
                                              sql_params=(status, condition_action, recurring_transaction_id))
     
    if current_user == recurring_transaction.sender_id and current_user == recurring_transaction.receiver_id:
        # updated_card_balance
        update_query(sql='UPDATE cards SET balance = balance - ? WHERE id = ?',
                     sql_params=(amount, cards_id))
    if current_user == sender_id and current_user != receiver_id:
        # updated_user_balance
        update_query(sql='UPDATE users SET balance = balance - ? WHERE id = ?',
                     sql_params=(amount, sender_id))
    if current_user == sender_id and current_user == receiver_id:
        # updated_user_balance
        update_query(sql='UPDATE users SET balance = balance + ? WHERE id = ?',
                     sql_params=(amount, receiver_id))

    sent_recurring_transactions = read_query(sql=id_recurring_transactions,
                                             sql_params=(recurring_transaction_id,))

    sent_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in sent_recurring_transactions), None)

    return sent_recurring_transaction


def preview_confirm_recurring_transaction(recurring_transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
    recurring_transactions = read_query(sql=id_recurring_transactions,
                                        sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    sender_id = recurring_transaction.sender_id
    receiver_id = recurring_transaction.receiver_id

    confirmed_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET status = ?, `condition` = ? WHERE id = ?',
                                                   sql_params=(status, condition_action, recurring_transaction_id))

    if current_user != sender_id and current_user == receiver_id:
        # updated_user_balance
        update_query(sql='UPDATE users SET balance = balance + ? WHERE id = ?',
                     sql_params=(amount, receiver_id))
          

    confirmed_recurring_transactions = read_query(sql=id_recurring_transactions,
                                                  sql_params=(recurring_transaction_id,))

    confirmed_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in confirmed_recurring_transactions), None)

    return confirmed_recurring_transaction


def preview_cancel_recurring_transaction(recurring_transaction_id: int, status: str, condition_action: str):
    recurring_transactions = read_query(sql=id_recurring_transactions,
                                        sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    cancelled_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET status = ?, `condition` = ? WHERE id = ?',
                                                   sql_params=(status, condition_action, recurring_transaction_id))
     

    cancelled_recurring_transactions = read_query(sql=id_recurring_transactions,
                                                  sql_params=(recurring_transaction_id,))

    cancelled_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in cancelled_recurring_transactions), None)

    return cancelled_recurring_transaction


def preview_decline_recurring_transaction(recurring_transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
    recurring_transactions = read_query(sql=id_recurring_transactions,
                                        sql_params=(recurring_transaction_id,))

    recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in recurring_transactions), None)

    if recurring_transaction is None:
        return None 

    declined_amount = recurring_transaction.amount
    sender = recurring_transaction.sender_id

    # updated_user_balance
    update_query(sql='UPDATE users SET balance = balance + ? WHERE id = ?',
                 sql_params=(declined_amount, sender))

    declined_recurring_transaction = update_query(sql='UPDATE recurring_transactions SET status = ?, `condition` = ? WHERE id = ?',
                                                  sql_params=(status, condition_action, recurring_transaction_id))
     

    declined_recurring_transactions = read_query(sql=id_recurring_transactions,
                                                 sql_params=(recurring_transaction_id,))

    declined_recurring_transaction = next((RecurringTransaction.from_query_result(*row) for row in declined_recurring_transactions), None)

    return declined_recurring_transaction


def recurring_transaction_id_exists(recurring_transaction_id: int):
    '''
    Explanation to follow.\n
    Parameters explanation to follow.
    '''
    return any(read_query(sql=id_recurring_transactions,
                                   sql_params=(recurring_transaction_id,)))


def user_id_exists(user_id: int):
    return any(read_query(sql='''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance 
                                          FROM users 
                                          WHERE id = ?''',
                                   sql_params=(user_id,)))


def get_user_by_id(user_id: int):
    user_data = read_query(sql='''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance
                                  FROM users
                                  WHERE id = ?''',
                           sql_params=(user_id,))
    
    user = next((User.from_query_result(*row) for row in user_data), None)

    return user


def get_category_by_id(category_id: int):
    category_data = read_query(sql='SELECT id, name FROM categories WHERE id = ?',
                               sql_params=(category_id,))

    category = next((Category.from_query_result(*row) for row in category_data), None)

    return category


def get_card_by_id(card_id: int):
    card_data = read_query(sql='''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                                  FROM cards
                                  WHERE id = ?''',
                           sql_params=(card_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    return card


def get_card_by_user_id(cards_user_id: int):
    card_data = read_query(sql='''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                                  FROM cards
                                  WHERE user_id = ?''',
                           sql_params=(cards_user_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    card_id = card.id

    return card_id
