from data.models.transactions import Transaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query

sql_transactions = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                      FROM transactions'''

sender_id_transactions = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                            FROM transactions
                            WHERE sender_id = ?'''

receiver_id_transactions = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                              FROM transactions
                              WHERE receiver_id = ?'''

id_transactions = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                     FROM transactions
                     WHERE id = ?'''

values_transactions = '''INSERT INTO transactions(id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id) 
                         VALUES(?,?,?,?,?,?,?,?,?)'''

def view_all_transactions(current_user: int, transaction_date: str, sender: str, receiver: str, direction: str):
     '''
     This function returns a list of all the transactions for the specified user.\n
     Parameters:\n
     - current_user: int\n
          - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
          - This parameter is used to ensure that the request is made by an authenticated user.\n
     - transaction_date: str | None\n
          - Filter transactions by a specific date.\n
     - sender: int | None\n
          - Filter transactions by the sender's user ID.\n
     - receiver: int | None\n
          - Filter transactions by the receiver's user ID.\n
     - direction: str | None\n
          - Filter transactions by direction ('incoming' or 'outgoing').\n
     '''
     if transaction_date or sender or receiver or direction:
          filter_by = []
          if transaction_date:
               filter_by.append(f'transaction_date like "%{transaction_date}%"')
          if sender:
               filter_by.append(f'sender_id like "%{sender}%"')
          if receiver:
               filter_by.append(f'receiver_id like "%{receiver}%"')
          if direction:
               if direction == 'outgoing' and current_user == receiver:
                    filter_by.append(f'sender_id like "%{current_user}%"')
               elif direction == 'incoming':
                    filter_by.append(f'receiver_id like "%{current_user}%"')

          if filter_by:
               sql_transactions += ' WHERE ' + ' AND '.join(filter_by)
          
          return (Transaction.from_query_result(*row) for row in read_query(sql=sql_transactions))
     
     else:
          transactions_incoming = read_query(sql=receiver_id_transactions,
                                             sql_params=(current_user,))
          transactions_outgoing = read_query(sql=sender_id_transactions,
                                             sql_params=(current_user,))
          transactions = transactions_incoming + transactions_outgoing

          transactions_all = []
          for row in transactions:
               transaction = Transaction.from_query_result(*row)
               if transaction not in transactions_all:
                    transactions_all.append(transaction)

          return transactions_all


def sort_transactions(transactions: list[Transaction], *, attribute='transaction_date', reverse=False):
     if attribute == 'transaction_date':
          def sort_fn(t: Transaction): return t.transaction_date
     if attribute == 'amount':
          def sort_fn(t: Transaction): return t.amount
     
     return sorted(transactions, key=sort_fn, reverse=reverse)


def view_transaction_by_id(transaction_id: int, current_user: int):
     '''
     This function returns a more detailed information about a user's transactions.\n
     Parameters:\n
     - transaction_id : int\n
          - The ID of the transaction to retrieve details for.\n
     - current_user : int\n
          - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
          - This parameter is used to ensure that the request is made by an authenticated user.
     '''
     transactions_outgoing = read_query(sql=sender_id_transactions,
                                        sql_params=(current_user,))
     transactions_incoming = read_query(sql=receiver_id_transactions,
                                        sql_params=(current_user,))
     transactions_all = transactions_outgoing + transactions_incoming

     if transactions_all:
          transaction_by_id = read_query(sql=id_transactions,
                                         sql_params=(transaction_id,))
     else:
          return None
     
     transaction = next((Transaction.from_query_result(*row) for row in transaction_by_id), None)

     if transaction is None:
          return None
     else:
          return transaction 


def create_transaction_to_users_wallet(transaction: Transaction, current_user: int):
     '''This function makes a transaction to the user wallet's ballance.
     Parameters:
     transaction : Transaction
        The transaction details to be added to the user's wallet.
     current_user: int
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        This parameter is used to ensure that the request is made by an authenticated user.
     '''
     sender_id = current_user
     receiver_id = current_user
     cards_user_id = current_user

     card_id = get_card_by_user_id(cards_user_id=cards_user_id)
     
     generated_id = insert_query(
                    sql=values_transactions,
                    sql_params=(transaction.id,
                                transaction.status, 
                                transaction.condition,
                                transaction.transaction_date,
                                transaction.amount,
                                transaction.category_name,
                                sender_id,
                                receiver_id,
                                card_id))

     transaction.id = generated_id

     return transaction


def create_transaction_to_users_balance(transaction: Transaction, current_user: int):
     '''
     This function makes a transaction to another user or category.\n
     Parameters:
     transaction : Transaction
        The transaction details to be added to the user's wallet.
     '''
     sender_id = current_user
     receiver_id = transaction.receiver_id
     cards_user_id = current_user

     card_id = get_card_by_user_id(cards_user_id=cards_user_id)

     generated_id = insert_query(
                    sql=values_transactions,
                    sql_params=(transaction.id,
                                transaction.status,
                                transaction.condition,
                                transaction.transaction_date,
                                transaction.amount,
                                transaction.category_name,
                                sender_id,
                                receiver_id,
                                card_id))

     transaction.id = generated_id

     return transaction


def create_transaction_to_users_category(transaction: Transaction, current_user: int):
     '''
     This function makes a transaction to another user or category.\n
     Parameters:
     transaction : Transaction
        The transaction details to be added to the user's wallet.
     '''
     sender_id = current_user
     receiver_id = transaction.receiver_id
     cards_user_id = current_user

     card_id = get_card_by_user_id(cards_user_id=cards_user_id)

     generated_id = insert_query(
                    sql=values_transactions,
                    sql_params=(transaction.id,
                                transaction.status, 
                                transaction.condition, 
                                transaction.transaction_date, 
                                transaction.amount,
                                transaction.category_name,
                                sender_id,
                                receiver_id,
                                card_id))

     transaction.id = generated_id

     return transaction


def preview_edited_transaction(transaction_id: int, new_amount: float, new_category_name: str, new_receiver_id: int):
     transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     if new_amount:
          edited_transaction = update_query(sql='UPDATE transactions SET amount = ? WHERE id = ?',
                                            sql_params=(new_amount, transaction_id))
     if new_category_name:
          edited_transaction = update_query(sql='UPDATE transactions SET category_name = ? WHERE id = ?',
                                            sql_params=(new_category_name, transaction_id))
     if new_receiver_id:
          edited_transaction = update_query(sql='UPDATE transactions SET reveiver_id = ? WHERE id = ?',
                                            sql_params=(new_receiver_id, transaction_id))
          
     edited_transactions = read_query(sql=id_transactions,
                                      sql_params=(transaction_id,))

     edited_transaction = next((Transaction.from_query_result(*row) for row in edited_transactions), None)

     return edited_transaction


def preview_sent_transaction(transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
     transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     sender_id = transaction.sender_id
     receiver_id = transaction.receiver_id
     cards_id = transaction.cards_id

     sent_transaction = update_query(sql='UPDATE transactions SET status = ?, `condition` = ? WHERE id = ?',
                                     sql_params=(status, condition_action, transaction_id))
     
     if current_user == transaction.sender_id and current_user == transaction.receiver_id:
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

     sent_transactions = read_query(sql=id_transactions,
                                    sql_params=(transaction_id,))

     sent_transaction = next((Transaction.from_query_result(*row) for row in sent_transactions), None)

     return sent_transaction


def preview_confirm_transaction(transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
     transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     sender_id = transaction.sender_id
     receiver_id = transaction.receiver_id

     confirmed_transaction = update_query(sql='UPDATE transactions SET status = ?, `condition` = ? WHERE id = ?',
                                          sql_params=(status, condition_action, transaction_id))

     if current_user != sender_id and current_user == receiver_id:
          # updated_user_balance
          update_query(sql='UPDATE users SET balance = balance + ? WHERE id = ?',
                       sql_params=(amount, receiver_id))
          
     confirmed_transactions = read_query(sql=id_transactions,
                                         sql_params=(transaction_id,))

     confirmed_transaction = next((Transaction.from_query_result(*row) for row in confirmed_transactions), None)

     return confirmed_transaction


def preview_cancel_transaction(transaction_id: int, status: str, condition_action: str):
     transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     cancelled_transaction = update_query(sql='UPDATE transactions SET status = ?, `condition` = ? WHERE id = ?',
                                          sql_params=(status, condition_action, transaction_id))
     
     cancelled_transactions = read_query(sql=id_transactions,
                                         sql_params=(transaction_id,))

     cancelled_transaction = next((Transaction.from_query_result(*row) for row in cancelled_transactions), None)

     return cancelled_transaction


def preview_decline_transaction(transaction_id: int, amount: float, status: str, condition_action: str, current_user: int):
     transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     declined_amount = transaction.amount
     sender = transaction.sender_id

     # updated_user_balance
     update_query(sql='UPDATE users SET balance = balance + ? WHERE id = ?',
                  sql_params=(declined_amount, sender))

     declined_transaction = update_query(sql='UPDATE transactions SET status = ?, `condition` = ? WHERE id = ?',
                                         sql_params=(status, condition_action, transaction_id))

     declined_transactions = read_query(sql=id_transactions,
                               sql_params=(transaction_id,))

     declined_transaction = next((Transaction.from_query_result(*row) for row in declined_transactions), None)

     return declined_transaction


def transaction_id_exists(transaction_id: int):
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     return any(read_query(sql=id_transactions,
                                    sql_params=(transaction_id,)))


def get_user_by_id(user_id: int):
    user_data = read_query(sql='''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance
                                  FROM users
                                  WHERE id = ?''',
                           sql_params=(user_id,))
    
    user = next((User.from_query_result(*row) for row in user_data), None)

    return user


def get_user_by_status(user_id: int) -> str:
     '''
     This function retrieves the status of a user from the database based on their user ID.
    
     Parameters:
     user_id : int
          The ID of the user whose status is being retrieved.

    '''
     user_status = read_query(sql='''SELECT status
                                     FROM users
                                     WHERE id = ?''',
                                     sql_params=(user_id,))
    
     user_status = next((row[0] for row in user_status), None)

     return user_status


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


def user_id_exists(user_id: int):
    return any(read_query(sql='''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance 
                                          FROM users 
                                          WHERE id = ?''',
                                   sql_params=(user_id,)))


def contact_id_exists(current_user: int, reciever_id: int):
     '''
     This function checks if a contact exists between the current user and the receiver.
     Parameters:
     current_user : int
          The ID of the current authenticated user.
     reciever_id : int
          The ID of the receiver to check the contact against.
     '''
     return any(read_query(sql='''SELECT users_id, contact_user_id
                                           FROM contacts 
                                           WHERE users_id = ? AND contact_user_id = ?''',
                                    sql_params=(current_user, reciever_id,)))