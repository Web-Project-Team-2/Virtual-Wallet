from data.models.transactions import Transaction
from data.models.user import User
from data.database_queries import read_query, insert_query, update_query
from schemas import transactions

def show_all_transactions(current_user: int):
     '''
     This function returns a list of all the transactions for the authenticated user.

     Parameters:
     current_user : int
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        This parameter is used to ensure that the request is made by an authenticated user.

     '''
     transactions = read_query('''SELECT id, status, transaction_date, amount, next_payment, categories_id, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE sender_id = ?''',
                               (current_user,))
     
     transactions_data = []
     for row in transactions:
          transaction = Transaction.from_query_result(*row)
          transaction.transaction_date = transaction.transaction_date.strftime('%Y/%m/%d %H:%M')
          transaction.next_payment = transaction.next_payment.strftime('%Y/%m/%d %H:%M')
          transactions_data.append(transaction)

     return transactions_data

def show_transaction_by_id(transaction_id: int):
     '''
     This finction returns a more detailed information about a user's transactions.

     Parameters:
     transaction_id : int
        The ID of the transaction to retrieve details for.

     current_user : int
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).
        This parameter is used to ensure that the request is made by an authenticated user.
     '''
     transactions = read_query('''SELECT id, status, transaction_date, amount, next_payment, categories_id, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE id = ?''',
                               (transaction_id,))
     
     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction:
          transaction.transaction_date = transaction.transaction_date.strftime('%Y/%m/%d %H:%M')
          transaction.next_payment = transaction.next_payment.strftime('%Y/%m/%d %H:%M')
     
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
                    '''INSERT INTO transactions(id, status, transaction_date, amount, next_payment, categories_id, sender_id, receiver_id, cards_id) 
                           VALUES(?,?,?,?,?,?,?,?,?)''',
                    (transaction.id,transaction.status, transaction.transaction_date, transaction.amount, transaction.next_payment,
                                transaction.categories_id, transaction.sender_id, transaction.receiver_id, transaction.cards_id))
     
     user_ballance = update_query(
                    '''UPDATE users SET balance = balance + ? WHERE id = ?''',
                    (transaction.amount, current_user))

     transaction.id = generated_id

     return transaction, user_ballance

def create_transactions(transaction: Transaction):
     '''
     This function makes a transaction to another user or category.\n

     Parameters:\n
     - receiver_id: int\n
        - The ID of the user who will receive the transaction.\n
     -  categories_id: int\n
        - The ID of the category to which the transaction is related.
     '''
     generated_id = insert_query(
                    '''INSERT INTO transactions(id, status, transaction_date, amount, next_payment, categories_id, sender_id, receiver_id, cards_id) 
                           VALUES(?,?,?,?,?,?,?,?,?)''',
                    (transaction.id,transaction.status, transaction.transaction_date, transaction.amount, transaction.next_payment,
                                transaction.categories_id, transaction.sender_id, transaction.receiver_id, transaction.cards_id))

     transaction.id = generated_id

     return transaction

# service which will check if a transaction exists - not cancelled by the sender?
def transaction_id_exists():
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     pass



