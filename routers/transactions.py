from fastapi import APIRouter, Depends, HTTPException, status, Query
from jose import JWTError
from datetime import datetime
from typing import List
from common.authorization import get_current_user
from common.responses import BadRequest, NotFound
from data.models.transactions import Transaction
from schemas.transactions import TransactionViewAll, TransactionView
from services import transactions_service


transactions_router = APIRouter(prefix='/transactions')


@transactions_router.get('/', response_model=List[TransactionViewAll], status_code=201, tags=['Transactions'])  
def get_users_transactions(sort: str | None = None, sort_by: str | None = None, 
                           page: int = Query(None, gt=0), transactions_per_page: int = Query(5, gt=0), 
                           transaction_date: str | None = None, 
                           direction: str | None = None,
                           sender: int | None = None, receiver: int | None = None,
                           current_user: int = Depends(get_current_user)):
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
   try:
      users_transactions = transactions_service.view_all_transactions(current_user, transaction_date, sender, receiver, direction)

      transactions_view = []
      for users_transaction in users_transactions:
         sender = transactions_service.get_user_by_id(users_transaction.sender_id)
         receiver = transactions_service.get_user_by_id(users_transaction.receiver_id)

         if current_user == sender.id and current_user == receiver.id:
            direction = 'incoming'
         elif current_user == sender.id: 
            direction = 'outgoing'
         elif current_user == receiver.id:
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
def get_transaction_by_id(transaction_id: int, current_user: int = Depends(get_current_user)):
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

      if current_user == sender.id and current_user == receiver.id:
         direction = 'incoming'
      if current_user == sender.id: 
         direction = 'outgoing'
      if current_user == receiver.id:
         direction = 'incoming'

      if not sender or not receiver:
            return NotFound(content='Required data not found.')
      
      if transaction_view is None:
         return NotFound(content=f'The transaction you are looking for is not available.')
      else:
         transaction_view = [TransactionView.transaction_view(transaction_view, sender, receiver,direction)]
         return transaction_view
      
   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')
   

@transactions_router.post('/wallet', status_code=201, tags=['Transactions']) 
def create_transaction_wallet(transaction: Transaction, current_user: int = Depends(get_current_user)):
   '''
   This function makes a transaction to the user wallet's ballance.\n
   Parameters:\n
   - transaction : Transaction\n
      - The transaction details to be added to the user's wallet.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   try:
      transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = current_user
      cards_user_id = current_user

      transaction_create = transactions_service.create_transaction_to_users_wallet(transaction, current_user)

      sender = transactions_service.get_user_by_id(sender_id)
      receiver = transactions_service.get_user_by_id(receiver_id)
      card_id = transactions_service.get_card_by_user_id(cards_user_id)

      if current_user == sender.id and current_user == receiver.id: 
         direction = 'incoming'

      if not sender or not receiver:
            return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction_create, sender, receiver,direction)]

      return transaction_create

   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.post('/user', status_code=201, tags=['Transactions']) 
def create_transaction_wallet(transaction: Transaction, current_user: int = Depends(get_current_user)):
   '''
   This function makes a transaction to the user wallet's ballance.\n
   Parameters:\n
   - transaction : Transaction\n
      - The transaction details to be added to the user's wallet.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   try:
      transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = transaction.receiver_id
      cards_user_id = current_user

      sender = transactions_service.get_user_by_id(sender_id)
      receiver = transactions_service.get_user_by_id(receiver_id)
      contact = transactions_service.contact_id_exists(current_user, transaction.receiver_id)
      receiver_status = transactions_service.get_user_by_status(receiver.id)
      card_id = transactions_service.get_card_by_user_id(cards_user_id)
      card_holder = transactions_service.get_card_by_id(card_id)
      card_number = transactions_service.get_card_by_id(card_id)

      if contact is not None and receiver_status != 'pending' and receiver_status != 'blocked':
         transaction_create = transactions_service.create_transaction_to_users_balance(transaction, current_user)
      else:
         return BadRequest(content=f'The contact is not available.')
      
      if current_user == sender.id: 
         direction = 'outgoing'

      if not sender or not receiver or not card_holder or not card_number:
         return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction_create, sender, receiver,direction)]

      return transaction_create

   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')
   

@transactions_router.post('/category', status_code=201, tags=['Transactions']) 
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
   try:
      transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = transaction.receiver_id
      cards_user_id = receiver_id

      transaction_create = transactions_service.create_transaction_to_users_ballnace(transaction, current_user)

      sender = transactions_service.get_user_by_id(sender_id)
      receiver = transactions_service.get_user_by_id(receiver_id)
      card_id = transactions_service.get_card_by_user_id(cards_user_id)
      card_holder = transactions_service.get_card_by_id(card_id)
      card_number = transactions_service.get_card_by_id(card_id)

      if current_user == sender.id: 
         direction = 'outgoing'

      if not sender or not receiver or not card_holder or not card_number:
            return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction_create, sender, receiver,direction, card_holder, card_number)]

      return transaction_create

   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.put('/preview/id/{transaction_id}', status_code=201, tags=['Transactions'])  
def preview_transaction(transaction_id: int, transaction: Transaction, current_user: int = Depends(get_current_user)):
   '''
   This function confirmes or declines a transaction.\n
   Parameters:\n
   - transaction_id : int\n
      - The ID of the transaction to retrieve details for.\n
   - current_user : int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   try:
      sender = transactions_service.get_user_by_id(transaction.sender_id)
      receiver = transactions_service.get_user_by_id(transaction.receiver_id)

      if current_user == sender.id and current_user == receiver.id:
         direction = 'incoming'
      elif current_user == sender.id and current_user != receiver.id: 
         direction = 'outgoing'
      elif current_user == receiver.id:
         direction = 'incoming'

      if not transactions_service.transaction_id_exists(transaction_id):
         return BadRequest(content=f'Transaction {transaction_id} does not exist.')

      condition_action = transaction.condition
      
      if current_user == sender.id and current_user == receiver.id:
         if condition_action == 'edited':
            new_amount = transaction.amount
            # category_name = transaction.category_name
            # receiver_id = transaction.receiver_id
            if new_amount:
               transaction_edited = transactions_service.preview_edited_transaction(transaction_id, new_amount)
               transaction_ready = transaction_edited
            # elif category_name:
            #    pass
            # elif receiver_id:
            #    pass
         elif condition_action == 'sent' and transaction.status == 'pending':
            amount = transaction.amount
            status = 'confirmed'
            transaction_sent = transactions_service.preview_sent_transaction(transaction_id, amount, status, condition_action, current_user)
            transaction_ready = transaction_sent
         elif condition_action == 'cancelled' and transaction.status == 'pending':
            status = 'declined'
            transaction_cancelled = transactions_service.preview_cancel_transaction(transaction_id,  status, condition_action)
            transaction_ready = transaction_cancelled
      
      transaction_view = [TransactionView.transaction_view(transaction_ready, sender, receiver,direction)]

      return transaction_view
   
   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')