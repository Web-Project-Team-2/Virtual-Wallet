from data.models.transactions import Transaction
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


# service which will add money to the balance attribute for the users column in the DB - 
def add_money_to_users_ballnace():
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     pass

# service which will create a transaction to the transactions column in the DB - create_transactions()
def create_transactions():
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     pass

# service which will check if a transaction exists - not cancelled by the sender?
def transaction_id_exists():
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     pass



