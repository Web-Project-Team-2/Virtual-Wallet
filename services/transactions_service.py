from data.models.transactions import Transaction
from data.models.user import User
from data.models.cards import Card
from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query
from schemas.transactions import TransactionViewAll
from common.responses import Unauthorized, NotFound, BadRequest

def view_all_transactions(current_user: int, transaction_date: str, sender: str, receiver: str, direction: str):
     '''
     This function returns a list of all the transactions for the specified user.\n
     Parameters:\n
     - sort: str | None\n
          - The sort order of the transactions. Acceptable values are 'asc' for ascending or 'desc' for descending.\n
     - sort_by: str | None\n
          - The attributes to sort the transactions are 'transaction_date' and 'amount'.\n
     - page: int | None\n
          - The page number to retrieve. If not specified, all transactions are returned.\n
     - transactions_per_page: int\n
          - The number of transactions per page. Default is 5.\n
     - transaction_date: str | None\n
          - Filter transactions by a specific date.\n
     - direction: str | None\n
          - Filter transactions by direction ('incoming' or 'outgoing').\n
     - sender: int | None\n
          - Filter transactions by the sender's user ID.\n
     - receiver: int | None\n
          - Filter transactions by the receiver's user ID.\n
     - current_user: int\n
          - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
          - This parameter is used to ensure that the request is made by an authenticated user.\n
     '''
     if transaction_date or sender or receiver or direction:
          sql = '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
               FROM transactions'''

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
               sql += ' WHERE ' + ' AND '.join(filter_by)
          
          return (Transaction.from_query_result(*row) for row in read_query(sql))
     
     else:
          transactions_incoming = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                             FROM transactions
                                             WHERE receiver_id = ?''',
                                        (current_user,))
          
          transactions_outgoing = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                             FROM transactions
                                             WHERE sender_id = ?''',
                                        (current_user,))
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
     transactions_out = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                          FROM transactions
                                          WHERE sender_id = ?''',
                                   (current_user,))
     transactions_in = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                         FROM transactions
                                         WHERE receiver_id = ?''',
                                  (current_user,))
     transactions_all = transactions_out + transactions_in

     if transactions_all:
          transaction_by_id = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
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

def create_transaction_to_users_ballnace(transaction: Transaction, current_user: int):
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

     card_id = get_card_by_user_id(cards_user_id)
     
     generated_id = insert_query(
                    '''INSERT INTO transactions(id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id) 
                           VALUES(?,?,?,?,?,?,?,?,?)''',
                    (transaction.id, transaction.status, transaction.condition, transaction.transaction_date, transaction.amount,
                                transaction.category_name, sender_id, receiver_id, card_id))
     
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
          '''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                 FROM transactions 
                 WHERE id = ?''',
          (transaction_id,)))

def preview_edited_transaction(transaction_id: int, new_amount: float):
     transactions = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     if new_amount:
          updated_transaction = update_query('UPDATE transactions SET amount = ? WHERE id = ?',
                                (new_amount, transaction_id))
     
     updated_transactions = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))

     updated_transaction = next((Transaction.from_query_result(*row) for row in updated_transactions), None)

     return updated_transaction

def preview_sent_transaction(transaction_id: int, amount: float, status: str, current_user: int):
     transactions = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     sender_id = transaction.sender_id
     receiver_id = transaction.receiver_id
     cards_id = transaction.cards_id

     updated_transaction = update_query('UPDATE transactions SET amount = ?, status = ? WHERE id = ?',
                                        (amount, status, transaction_id))
     
     # updated_card_balance
     update_query('UPDATE cards SET balance = balance + ? WHERE id = ?',
                                         (amount, cards_id))
     
     if current_user == sender_id and current_user != receiver_id:
          # updated_user_balance
          update_query('UPDATE users SET balance = balance - ? WHERE id = ?',
                                              (amount, sender_id))
     if current_user == sender_id and current_user == receiver_id:
          # updated_user_balance
          update_query('UPDATE users SET balance = balance + ? WHERE id = ?',
                                              (amount, receiver_id))

     updated_transactions = read_query('''SELECT id, status, `condition`, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))

     updated_transaction = next((Transaction.from_query_result(*row) for row in updated_transactions), None)

     return updated_transaction

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

def get_card_by_user_id(cards_user_id: int):
    card_data = read_query('''SELECT id, card_number, cvv, card_holder, expiration_date, card_status, user_id, balance
                              FROM cards
                              WHERE user_id = ?''', (cards_user_id,))
    
    card = next((Card.from_query_result(*row) for row in card_data), None)

    card_id = card.id

    return card_id


def user_id_exists(user_id: int):
    return any(read_query(
        '''SELECT id, email, username, password, phone_number, is_admin, create_at, status, balance 
               FROM users 
               WHERE id = ?''',
        (user_id,)))