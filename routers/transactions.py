from fastapi import APIRouter, Depends, HTTPException, status, Query
from jose import JWTError
from common.responses import BadRequest, NotFound
from common.authorization import get_current_user
from data.models.transactions import Transaction
from schemas.transactions import TransactionViewAll, TransactionView
from services import transactions_service
from datetime import datetime
from typing import List


transactions_router = APIRouter(prefix='/transactions')


@transactions_router.get('/', response_model=List[TransactionViewAll], status_code=201, tags=['Transactions'])  
def get_users_transactions(sort: str | None = None, sort_by: str | None = None, 
                           page: int = Query(None, gt=0), transactions_per_page: int = Query(10, gt=0), 
                           transaction_date: str | None = None, 
                           direction: str | None = None,
                           sender: int | None = None, receiver: int | None = None,
                           current_user: int = Depends(get_current_user)):
   '''
   This function returns a list of all the transactions for the specified user.\n

    Parameters:\n
    - sort: str | None\n
        The sort order of the transactions. Acceptable values are 'asc' for ascending or 'desc' for descending.\n
    - sort_by: str | None\n
        The attribute to sort the transactions 'transaction_date' and 'amount'.\n
    - page: int | None\n
        The page number to retrieve. If not specified, all transactions are returned.\n
    - transactions_per_page: int\n
        The number of transactions per page. Default is 10.\n
    - transaction_date: str | None\n
        Filter transactions by a specific date.\n
    - direction: str | None\n
        Filter transactions by direction ('incoming' or 'outgoing').\n
    - sender: int | None\n
        Filter transactions by the sender's user ID.\n
    - receiver: int | None\n
        Filter transactions by the receiver's user ID.\n
    - current_user: int\n
        The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        This parameter is used to ensure that the request is made by an authenticated user.\n
   ''' 
   try:
      users_transactions = transactions_service.view_all_transactions(current_user, transaction_date, sender, receiver, direction)

      transactions_view = []
      for users_transaction in users_transactions:
         sender = transactions_service.get_user_by_id(users_transaction.sender_id)
         receiver = transactions_service.get_user_by_id(users_transaction.receiver_id)

         if current_user == sender.id: 
            direction = 'outgoing'
         if current_user == receiver.id:
            direction = 'incoming'

         if not sender or not receiver:
               return NotFound(content='Required data not found.')
         
         transactions_view.append(TransactionViewAll.transactions_view(users_transaction, sender, receiver, direction))
      
      if page:
         start = (page - 1) * transactions_per_page
         end = start + transactions_per_page
         transactions_view = transactions_view[start:end]

      if sort and (sort == 'asc' or sort == 'desc'):
         return transactions_service.sort_transactions(transactions_view, reverse=sort == 'desc', attribute=sort_by)
      else:
         return transactions_view

   except JWTError:
      raise HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.get('/id/{transaction_id}', response_model=List[TransactionView], status_code=201, tags=['Transactions']) 
def get_transactions_by_id(transaction_id: int, current_user: int = Depends(get_current_user)):
   '''
   This function returns a more detailed information about a user's transactions.\n

   Parameters:\n
   - transaction_id : int\n
      - The ID of the transaction to retrieve details for.\n
   - current_user : int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   try:
      transaction_view = transactions_service.view_transaction_by_id(transaction_id, current_user)
      sender = transactions_service.get_user_by_id(transaction_view.sender_id)
      receiver = transactions_service.get_user_by_id(transaction_view.receiver_id)
      card_holder = transactions_service.get_card_by_id(transaction_view.cards_id)
      card_number = transactions_service.get_card_by_id(transaction_view.cards_id)

      if current_user == sender.id: 
         direction = 'outgoing'
      if current_user != sender.id:
         direction = 'incoming'

      if not sender or not receiver or not card_holder or not card_number:
            return NotFound(content='Required data not found.')
      
      if transaction_view is None:
         return NotFound(content=f'The transaction you are looking for is not available.')
      else:
         transaction_view = [TransactionView.transaction_view(transaction_view, sender, receiver,direction, card_holder, card_number)]
         return transaction_view
      
   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')
   

@transactions_router.post('/wallet', status_code=201, tags=['Transactions']) 
def add_money_to_wallet(transaction: Transaction, current_user: int = Depends(get_current_user)):
   '''This function makes a transaction to the user wallet's ballance.\n

   Parameters:\n
   - transaction : Transaction\n
      - The transaction details to be added to the user's wallet.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   try:
      transaction.transaction_date = datetime.now()

      sender_id = int(transaction.sender_id)
      receiver_id = int(transaction.receiver_id)
      card_id = int(transaction.cards_id)

      transaction_create = transactions_service.add_money_to_users_ballnace(transaction)
      sender = transactions_service.get_user_by_id(sender_id)
      receiver = transactions_service.get_user_by_id(receiver_id)
      card_holder = transactions_service.get_card_by_id(card_id)
      card_number = transactions_service.get_card_by_id(card_id)

      if current_user == sender.id and current_user == receiver.id: 
         direction = 'incoming'

      if not sender or not receiver or not card_holder or not card_number:
            return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction_create, sender, receiver,direction, card_holder, card_number)]

      return transaction_create

   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')

@transactions_router.post('/', status_code=201, tags=['Transactions']) 
def make_a_transaction(transaction: Transaction, current_user: int = Depends(get_current_user)):
   '''
   This function makes a transaction to another user or category.\n

   Parameters:\n
   - transaction : Transaction\n
      - The transaction details to be added to the user's wallet.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''

   transaction.transaction_date = datetime.now()
   transaction.transaction_date = transaction.transaction_date.strftime("%Y/%m/%d %H:%M")

   transaction.receiver_id = transactions_service.user_id_exists(transaction.receiver_id)
   transaction.categories_id = transactions_service.get_category_by_id(transaction.categories_id)

   if transaction.receiver_id and transaction.categories_id:
      return transactions_service.create_transactions(transaction)

@transactions_router.put('/approval/id/{transaction_id}', status_code=201, tags=['Transactions'])  
def approve_a_transaction(transaction_id: int, current_user: int = Depends(get_current_user)):
   '''
   This function confirmes or declines a transaction.\n

   Parameters:\n
   - transaction_id : int\n
      - The ID of the transaction to retrieve details for.\n
   - current_user : int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   if not transactions_service.transaction_id_exists(transaction_id):
      return BadRequest(content=f'Transaction {transaction_id} does not exist.')

   transaction = transactions_service.approve_transaction(transaction_id)
   return transaction