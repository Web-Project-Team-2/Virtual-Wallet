from data.models.transactions import Transaction
from data.database_queries import read_query, insert_query, update_query
from common.responses import BadRequest
from services import cards_services
from datetime import datetime

sql_transactions = '''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                      FROM transactions'''

sender_id_transactions = '''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                            FROM transactions
                            WHERE sender_id = $1'''

receiver_id_transactions = '''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                              FROM transactions
                              WHERE receiver_id = $1'''

id_transactions = '''SELECT id, status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id
                     FROM transactions
                     WHERE id = $1'''

values_transactions = '''INSERT INTO transactions(status, condition, transaction_date, amount, category_name, sender_id, receiver_id, cards_id) 
                         VALUES($1, $2, $3, $4, $5, $6, $7, $8)'''


async def view_all_transactions(current_user: int,
                                transaction_date: str | None = None,
                                sender: str | None = None,
                                receiver: str | None = None,
                                direction: str | None = None):
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

     sql_parameters = []
     loc_sql_transactions = sql_transactions

     if transaction_date or sender or receiver or direction:
          filter_by = []
          if transaction_date:
               try:
                    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
               except ValueError:
                    return BadRequest(content=f'Incorrect date format, should be YYYY-MM-DD.')
               filter_by.append(f'DATE(transaction_date) = ${len(sql_parameters) + 1}')
               sql_parameters.append(transaction_date)
          if sender:
               filter_by.append(f'sender_id = ${len(sql_parameters) + 1}')
               sql_parameters.append(sender)
          if receiver:
               filter_by.append(f'receiver_id = ${len(sql_parameters) + 1}')
               sql_parameters.append(receiver)
          if direction:
               if direction == 'outgoing' and current_user == receiver:
                    filter_by.append(f'sender_id = ${len(sql_parameters) + 1}')
                    sql_parameters.append(current_user)
               elif direction == 'incoming':
                    filter_by.append(f'receiver_id = ${len(sql_parameters) + 1}')
                    sql_parameters.append(current_user)

          if filter_by:
               loc_sql_transactions += ' WHERE ' + ' AND '.join(filter_by)

          sql_parameters = tuple(sql_parameters)
          rows = await read_query(sql=loc_sql_transactions,
                                  sql_params=sql_parameters)

          if rows != []:
               return [Transaction.from_query_result(*row) for row in rows]
          else:
               return None

     else:
          transactions_incoming = await read_query(sql=receiver_id_transactions,
                                                   sql_params=(current_user,))
          transactions_outgoing = await read_query(sql=sender_id_transactions,
                                                   sql_params=(current_user,))
          transactions = transactions_incoming + transactions_outgoing

          transactions_all = []
          for row in transactions:
               transaction = Transaction.from_query_result(*row)
               if transaction not in transactions_all:
                    transactions_all.append(transaction)

          if transactions_all != []:
               return transactions_all
          else:
               return None


def sort_transactions(transactions: list[Transaction], *,
                      attribute='transaction_date',
                      reverse=False):
     '''
     This function sorts a list of recurring transactions based on a specified attribute.\n
     Parameters:\n
     - recurring_transactions: list[RecurringTransaction]\n
          - A list of RecurringTransaction objects to be sorted.\n
     - attribute: str\n
          - The attribute to sort the transactions by. Default is 'recurring_transaction_date'.\n
     - reverse: bool\n
          - Whether to sort in reverse order. Default is False (ascending order).
     '''
     
     if attribute == 'transaction_date':
          def sort_fn(t: Transaction): return t.transaction_date
     elif attribute == 'amount':
          def sort_fn(t: Transaction): return t.amount
     else:
        return BadRequest(content=f'Unsupported sort attribute: {attribute}.')

     return sorted(transactions, key=sort_fn, reverse=reverse)


async def view_transaction_by_id(transaction_id: int,
                                 current_user: int):
     '''
     This function returns a more detailed information about a user's transactions.\n
     Parameters:\n
     - transaction_id : int\n
          - The ID of the transaction to retrieve details for.\n
     - current_user : int\n
          - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
          - This parameter is used to ensure that the request is made by an authenticated user.
     '''

     transactions_outgoing = await read_query(sql=sender_id_transactions,
                                              sql_params=(current_user,))
     transactions_incoming = await read_query(sql=receiver_id_transactions,
                                              sql_params=(current_user,))
     transactions_all = transactions_outgoing + transactions_incoming

     if transactions_all:
          transaction_by_id = await read_query(sql=id_transactions,
                                               sql_params=(transaction_id,))
     else:
          return None
     
     transaction = next((Transaction.from_query_result(*row) for row in transaction_by_id), None)

     return transaction 


async def create_transaction_to_users_wallet(transaction: Transaction,
                                             current_user: int):
     '''
     This function makes a transaction to the user wallet's ballance.\n
     Parameters:\n
     - transaction : Transaction\n
        - The transaction details to be added to the user's wallet.\n
     - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
     '''

     sender_id = current_user
     receiver_id = current_user
     cards_user_id = current_user

     card_id = await cards_services.get_card_by_user_id(cards_user_id=cards_user_id)
     
     generated_id = await insert_query(sql=values_transactions,
                                       sql_params=(transaction.status, 
                                                   transaction.condition,
                                                   transaction.transaction_date,
                                                   transaction.amount,
                                                   transaction.category_name,
                                                   sender_id,
                                                   receiver_id,
                                                   card_id))

     transaction.id = generated_id

     if transaction is not None:
          return transaction
     else:
          return None


async def create_transaction_to_users_balance(transaction: Transaction,
                                              current_user: int):
     '''
     This function makes a transaction to another user's balance.\n
     Parameters:\n
     - transaction : Transaction\n
        - The transaction details to be added to the user's balance.\n
     - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
     '''

     sender_id = current_user
     receiver_id = transaction.receiver_id
     cards_user_id = current_user

     card_id = await cards_services.get_card_by_user_id(cards_user_id=cards_user_id)

     generated_id = await insert_query(sql=values_transactions,
                                       sql_params=(transaction.status,
                                                   transaction.condition,
                                                   transaction.transaction_date,
                                                   transaction.amount,
                                                   transaction.category_name,
                                                   sender_id,
                                                   receiver_id,
                                                   card_id))

     transaction.id = generated_id

     if transaction is not None:
          return transaction
     else:
          return None


async def create_transaction_to_users_category(transaction: Transaction,
                                               current_user: int):
     '''
     This function makes a transaction to another user or category.\n
     Parameters:\n
     - transaction : Transaction\n
        - The transaction details to be added to the user's balance.\n
     - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
     '''

     sender_id = current_user
     receiver_id = transaction.receiver_id
     cards_user_id = current_user

     card_id = await cards_services.get_card_by_user_id(cards_user_id=cards_user_id)

     generated_id = await insert_query(sql=values_transactions,
                                       sql_params=(transaction.status, 
                                                   transaction.condition, 
                                                   transaction.transaction_date, 
                                                   transaction.amount,
                                                   transaction.category_name,
                                                   sender_id,
                                                   receiver_id,
                                                   card_id))

     transaction.id = generated_id

     if transaction is not None:
          return transaction
     else:
          return None


async def preview_edited_transaction(transaction_id: int,
                                     new_amount: float | None = None,
                                     new_category_name: str | None = None,
                                     new_receiver_id: int | None = None):
     '''
     Preview the edited transaction with the given parameters.\n
     Parameters:\n
     - transaction_id : int\n
          - The ID of the transaction to be previewed.\n
     - new_amount : float\n
          - The new amount for the transaction. If None, the amount remains unchanged.\n
     - new_category_name : str\n
          - The new category name for the transaction. If None, the category remains unchanged.\n
     - new_receiver_id : int\n
          - The new receiver ID for the transaction. If None, the receiver remains unchanged.
     '''

     transactions = await read_query(sql=id_transactions,
                                     sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None

     if new_amount is not None:
          edited_transaction = await update_query(sql='UPDATE transactions SET amount = $1 WHERE id = $2',
                                                  sql_params=(new_amount, transaction_id))
     if new_category_name is not None:
          edited_transaction = await update_query(sql='UPDATE transactions SET category_name = $1 WHERE id = $2',
                                                  sql_params=(new_category_name, transaction_id))
     if new_receiver_id is not None:
          edited_transaction = await update_query(sql='UPDATE transactions SET receiver_id = $1 WHERE id = $2',
                                                  sql_params=(new_receiver_id, transaction_id))
          
     edited_transactions = await read_query(sql=id_transactions,
                                            sql_params=(transaction_id,))

     edited_transaction = next((Transaction.from_query_result(*row) for row in edited_transactions), None)

     return edited_transaction


async def preview_sent_transaction(transaction_id: int,
                                   amount: float,
                                   status: str,
                                   condition_action: str,
                                   current_user: int):
     '''
     Preview a sent transaction with the given parameters.\n
     Parameters:\n
     - transaction_id : int\n
          - The ID of the transaction to be previewed.\n
     - amount : float\n
          - The amount of the transaction.\n
     - status : str\n
          - The new status for the transaction.\n
     - condition_action : str\n
          - The new condition of the transaction.\n
     - current_user : int\n
          - The ID of the current user initiating the preview.
     '''
     transactions = await read_query(sql=id_transactions,
                                     sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     sender_id = transaction.sender_id
     receiver_id = transaction.receiver_id
     cards_id = transaction.cards_id

     sent_transaction = await update_query(sql='UPDATE transactions SET status = $1, condition = $2 WHERE id = $3',
                                           sql_params=(status, condition_action, transaction_id))
     
     if current_user == transaction.sender_id and current_user == transaction.receiver_id:
          # updated_card_balance
          await update_query(sql='UPDATE cards SET balance = balance - $1 WHERE id = $2',
                       sql_params=(amount, cards_id))
     if current_user == sender_id and current_user != receiver_id:
          # updated_user_balance
          await update_query(sql='UPDATE users SET balance = balance - $1 WHERE id = $2',
                       sql_params=(amount, sender_id))
     if current_user == sender_id and current_user == receiver_id:
          # updated_user_balance
          await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                       sql_params=(amount, receiver_id))

     sent_transactions = await read_query(sql=id_transactions,
                                          sql_params=(transaction_id,))

     sent_transaction = next((Transaction.from_query_result(*row) for row in sent_transactions), None)

     return sent_transaction


async def preview_confirmed_transaction(transaction_id: int,
                                      amount: float,
                                      status: str,
                                      condition_action: str,
                                      current_user: int):
     '''
     This function previews a recurring transaction if it will be confirmed.\n
     Parameters:\n
     - transaction_id : int\n
        - The ID of the transaction to retrieve details for.\n
     - amount: float\n
        - The amount to be updated in the recurring transaction.\n
     - status: str\n
        - The new status of the recurring transaction.\n
     - condition_action: str\n
        - The new condition of the recurring transaction.\n
     - current_user: int\n
        - The ID of the currently authenticated user.
     '''
     
     transactions = await read_query(sql=id_transactions,
                                     sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     sender_id = transaction.sender_id
     receiver_id = transaction.receiver_id

     confirmed_transaction = await update_query(sql='UPDATE transactions SET status = $1, condition = $2 WHERE id = $3',
                                                sql_params=(status, condition_action, transaction_id))

     if current_user != sender_id and current_user == receiver_id:
          updated_user_balance = await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                                                    sql_params=(amount, receiver_id))
          
     confirmed_transactions = await read_query(sql=id_transactions,
                                               sql_params=(transaction_id,))

     confirmed_transaction = next((Transaction.from_query_result(*row) for row in confirmed_transactions), None)

     return confirmed_transaction


async def preview_cancelled_transaction(transaction_id: int,
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
     
     transactions = await read_query(sql=id_transactions,
                                     sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     cancelled_transaction = await update_query(sql='UPDATE transactions SET status = $1, condition = $2 WHERE id = $3',
                                                sql_params=(status, condition_action, transaction_id))
     
     cancelled_transactions = await read_query(sql=id_transactions,
                                               sql_params=(transaction_id,))

     cancelled_transaction = next((Transaction.from_query_result(*row) for row in cancelled_transactions), None)

     return cancelled_transaction


async def preview_declined_transaction(transaction_id: int,
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
     transactions = await read_query(sql=id_transactions,
                                     sql_params=(transaction_id,))

     transaction = next((Transaction.from_query_result(*row) for row in transactions), None)

     if transaction is None:
        return None 

     declined_amount = amount
     sender = transaction.sender_id
     receiver = current_user

     updated_user_balance = await update_query(sql='UPDATE users SET balance = balance + $1 WHERE id = $2',
                                               sql_params=(declined_amount, sender))

     declined_transaction = await update_query(sql='UPDATE transactions SET status = $1, condition = $2 WHERE id = $3',
                                               sql_params=(status, condition_action, transaction_id))

     declined_transactions = await read_query(sql=id_transactions,
                                              sql_params=(transaction_id,))

     declined_transaction = next((Transaction.from_query_result(*row) for row in declined_transactions), None)

     return declined_transaction


async def transaction_id_exists(transaction_id: int) -> bool:
     '''
     This function checks if a recurring transaction with the specified ID exists in the database.\n
     Parameters:\n
     - recurring_transaction_id: int\n
     - The ID of the recurring transaction to check for existence.
     '''
     return any(await read_query(sql=id_transactions,
                                          sql_params=(transaction_id,)))