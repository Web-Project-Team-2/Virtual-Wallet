from data.models.transactions import Transaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query
from schemas.transactions import TransactionViewAll
from common.responses import Unauthorized, NotFound, BadRequest

def view_all_transactions(current_user: int, transaction_date: str, sender: str, receiver: str, direction: str):
     '''
     This function returns a list of all the transactions for the authenticated user.

     Parameters:
     current_user : int
          The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
          This parameter is used to ensure that the request is made by an authenticated user.

     '''
     # sql = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
     #          FROM transactions'''

     # filter_by = [f'(sender_id = {current_user} OR receiver_id = {current_user})']

     # if transaction_date:
     #      filter_by .append(f"DATE(transaction_date) = '{transaction_date}'")
     # if sender:
     #      filter_by .append(f"sender_id = {sender}")
     # if receiver:
     #      filter_by .append(f"receiver_id = {receiver}")
     # if direction:
     #      if direction == 'outgoing':
     #           filter_by .append(f"sender_id = {current_user}")
     #      elif direction == 'incoming':
     #           filter_by .append(f"receiver_id = {current_user}")

     # if filter_by :
     #      sql += ' WHERE ' + ' AND '.join(filter_by)

     transactions_outgoing = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                          FROM transactions
                                          WHERE sender_id = ?''',
                                   (current_user,))
     
     transactions_incoming = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                         FROM transactions
                                         WHERE receiver_id = ?''',
                                   (current_user,))
     
     transactions = transactions_outgoing + transactions_incoming

     transactions_all = []
     for row in transactions:
          transaction = Transaction.from_query_result(*row)
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
     This finction returns a more detailed information about a user's transactions.

     Parameters:
     transaction_id : int
        The ID of the transaction to retrieve details for.

     current_user : int
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        This parameter is used to ensure that the request is made by an authenticated user.
     '''
     transactions_out = read_query('''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                          FROM transactions
                                          WHERE sender_id = ?''',
                                   (current_user,))
     transactions_in = read_query('''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                         FROM transactions
                                         WHERE receiver_id = ?''',
                                  (current_user,))
     transactions_all = transactions_out + transactions_in

     if transactions_all:
          transaction_by_id = read_query('''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                                FROM transactions
                                                WHERE id = ?''',
                                         (transaction_id,))
     else:
          return None
     
     transaction = next((Transaction.from_query_result(*row) for row in transaction_by_id), None)

     if transaction is None:
          return None
     else:
          return transaction 

def add_money_to_users_ballnace(transaction: Transaction, current_user: int):
     '''This function makes a transaction to the user wallet's ballance.

     Parameters:
     transaction : Transaction
        The transaction details to be added to the user's wallet.
     current_user: int
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        This parameter is used to ensure that the request is made by an authenticated user.
     '''
     generated_id = insert_query(
                    '''INSERT INTO transactions(id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id) 
                           VALUES(?,?,?,?,?,?,?,?,?)''',
                    (transaction.id,transaction.status, transaction.condition, transaction.transaction_date, transaction.amount,
                                transaction.category_name, transaction.sender_id, transaction.receiver_id, transaction.cards_id))
     
     # user_ballance = update_query(
     #                '''UPDATE users SET balance = balance + ? WHERE id = ?''',
     #                (transaction.amount, current_user))

     transaction.id = generated_id

     return transaction

def create_transactions(transaction: Transaction):
     '''
     This function makes a transaction to another user or category.\n

     Parameters:
     transaction : Transaction
        The transaction details to be added to the user's wallet.
     '''
     generated_id = insert_query(
                    '''INSERT INTO transactions(id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id) 
                           VALUES(?,?,?,?,?,?,?,?,?)''',
                    (transaction.id,transaction.status, transaction.condition, transaction.transaction_date, transaction.amount,
                                transaction.category_name, transaction.sender_id, transaction.receiver_id, transaction.cards_id))

     transaction.id = generated_id

     return transaction

def transaction_id_exists(transaction_id: int):
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     return any(
     read_query(
          '''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                 FROM transactions 
                 WHERE id = ?''',
          (transaction_id,)))

def approve_transaction(transaction_id: int):
     transactions = read_query('''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)
     update_query('UPDATE transactions SET status=%s WHERE id = %s',
                 (transaction_id))

     return transaction


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



