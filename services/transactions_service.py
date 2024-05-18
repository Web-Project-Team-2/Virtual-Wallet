from data.models.transactions import Transaction
from data.database_queries import read_query, insert_query, update_query
from schemas import transactions

# service which will get from the DB all of the transactions a list - 
def show_all_transactions(sender_id: int):
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     transactions = read_query('''SELECT id, status, transaction_date, amount, next_payment, categories_id, sender_id, receiver_id, cards_id
                                      FROM transactions
                                      WHERE sender_id= ?''',
                               (sender_id,))
     
     transactions_data = []
     for row in transactions:
          transaction = Transaction.from_query_result(*row)
          transaction.transaction_date = transaction.transaction_date.strftime('%Y/%m/%d %H:%M')
          transactions_data.append(transaction)

     return transactions_data

# service which will get from the DB a single transactions and all of its attributes - 
def show_transaction_by_id():
     '''Explanation to follow.\n
     Parameters explanation to follow.
     '''
     pass

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



