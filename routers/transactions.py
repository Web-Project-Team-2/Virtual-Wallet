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


@transactions_router.get(path='/', response_model=List[TransactionViewAll], status_code=201, tags=['Transactions'])  
async def get_users_transactions(sort: str | None = None,
                           sort_by: str | None = None, 
                           page: int = Query(default=None, gt=0),
                           transactions_per_page: int = Query(default=5, gt=0), 
                           transaction_date: str | None = None, 
                           direction: str | None = None,
                           sender: int | None = None,
                           receiver: int | None = None,
                           current_user: int = Depends(dependency=get_current_user)):
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
      - This parameter is used to ensure that the request is made by an authenticated user.
   ''' 
   try:
      users_transactions = await transactions_service.view_all_transactions(current_user=current_user,
                                                                      transaction_date=transaction_date,
                                                                      sender=sender,
                                                                      receiver=receiver,
                                                                      direction=direction)

      transactions_view = []
      for users_transaction in users_transactions:
         sender = await transactions_service.get_user_by_id(user_id=users_transaction.sender_id)
         receiver = await transactions_service.get_user_by_id(user_id=users_transaction.receiver_id)

         if current_user == sender.id and current_user == receiver.id:
            direction = 'incoming'
         elif current_user == sender.id: 
            direction = 'outgoing'
         elif current_user == receiver.id:
            direction = 'incoming'
            
         if not sender or not receiver:
            return NotFound(content='Required data not found.')
         
         transactions_view.append(TransactionViewAll.transactions_view(transaction=users_transaction,
                                                                              sender=sender,
                                                                              receiver=receiver,
                                                                              direction=direction))
      
      if page:
         start = (page - 1) * transactions_per_page
         end = start + transactions_per_page
         transactions_view = transactions_view[start:end]

      if sort and (sort == 'asc' or sort == 'desc'):
         return await transactions_service.sort_transactions(transactions=transactions_view,
                                                       reverse=sort == 'desc',
                                                       attribute=sort_by)
      else:
         return transactions_view

   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.get(path='/id/{transaction_id}', response_model=List[TransactionView], status_code=201, tags=['Transactions']) 
async def get_transaction_by_id(transaction_id: int, current_user: int = Depends(dependency=get_current_user)):
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
      transaction_view = await transactions_service.view_transaction_by_id(transaction_id=transaction_id,
                                                                     current_user=current_user)
      sender = await  transactions_service.get_user_by_id(user_id=transaction_view.sender_id)
      receiver = await transactions_service.get_user_by_id(user_id=transaction_view.receiver_id)

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
         transaction_view = [TransactionView.transaction_view(transaction=transaction_view,
                                                              sender=sender,
                                                              receiver=receiver,
                                                              direction=direction)]
         return transaction_view
      
   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Your session has expired. Please log in again to continue using the application.')
   

@transactions_router.post(path='/wallet', status_code=201, tags=['Transactions']) 
async def create_transaction_wallet(transaction: Transaction, current_user: int = Depends(dependency=get_current_user)):
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
      if not transaction.transaction_date:
         transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = current_user
      cards_user_id = current_user

      transaction_create = await transactions_service.create_transaction_to_users_wallet(transaction=transaction,
                                                                                   current_user=current_user)

      sender = await transactions_service.get_user_by_id(user_id=sender_id)
      receiver = await transactions_service.get_user_by_id(user_id=receiver_id)
      card_id = await transactions_service.get_card_by_user_id(cards_user_id=cards_user_id)

      if current_user == sender.id and current_user == receiver.id: 
         direction = 'incoming'

      if not sender or not receiver:
            return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction=transaction_create,
                                                             sender=sender,
                                                             receiver=receiver,
                                                             direction=direction)]

      return transaction_create

   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.post(path='/user', status_code=201, tags=['Transactions']) 
async def create_transaction_wallet(transaction: Transaction, current_user: int = Depends(dependency=get_current_user)):
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
      if not transaction.transaction_date:
         transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = transaction.receiver_id
      cards_user_id = current_user

      sender = await transactions_service.get_user_by_id(user_id=sender_id)
      receiver = await transactions_service.get_user_by_id(user_id=receiver_id)
      contact = await transactions_service.contact_id_exists(current_user=current_user,
                                                       reciever_id=transaction.receiver_id)
      receiver_status = await transactions_service.get_user_by_status(user_id=receiver.id)
      card_id = await transactions_service.get_card_by_user_id(cards_user_id=cards_user_id)
      card_holder = await transactions_service.get_card_by_id(card_id=card_id)
      card_number = await transactions_service.get_card_by_id(card_id=card_id)

      if contact is not None and receiver_status != 'pending' and receiver_status != 'blocked':
         transaction_create = await transactions_service.create_transaction_to_users_balance(transaction=transaction,
                                                                                       current_user=current_user)
      else:
         return BadRequest(content=f'The contact is not available.')
      
      if current_user == sender.id: 
         direction = 'outgoing'

      if not sender or not receiver or not card_holder or not card_number:
         return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction=transaction_create,
                                                             sender=sender,
                                                             receiver=receiver,
                                                             direction=direction)]

      return transaction_create

   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Your session has expired. Please log in again to continue using the application.')
   

@transactions_router.post(path='/category', status_code=201, tags=['Transactions']) 
async def make_a_transaction(transaction: Transaction, current_user: int = Depends(dependency=get_current_user)):
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
      if not transaction.transaction_date:
         transaction.transaction_date = datetime.now()

      sender_id = current_user
      receiver_id = transaction.receiver_id
      cards_user_id = receiver_id

      transaction_create = await transactions_service.create_transaction_to_users_category(transaction=transaction,
                                                                                     current_user=current_user)

      sender = await transactions_service.get_user_by_id(user_id=sender_id)
      receiver = await transactions_service.get_user_by_id(user_id=receiver_id)
      card_id = await transactions_service.get_card_by_user_id(cards_user_id=cards_user_id)
      card_holder = await transactions_service.get_card_by_id(card_id=card_id)
      card_number = await transactions_service.get_card_by_id(card_id=card_id)

      if current_user == sender.id: 
         direction = 'outgoing'

      if not sender or not receiver or not card_holder or not card_number:
            return NotFound(content='Required data not found.')
      
      transaction_create = [TransactionView.transaction_view(transaction=transaction_create,
                                                             sender=sender,
                                                             receiver=receiver,
                                                             direction=direction)]

      return transaction_create

   except JWTError:
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired. Please log in again to continue using the application.')


@transactions_router.put(path='/preview/id/{transaction_id}', status_code=201, tags=['Transactions'])  
async def preview_transaction(transaction_id: int, transaction: Transaction, current_user: int = Depends(dependency=get_current_user)):
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
      if await transactions_service.transaction_id_exists(transaction_id=transaction_id):
         sender = await transactions_service.get_user_by_id(user_id=transaction.sender_id)
         receiver = await transactions_service.get_user_by_id(user_id=transaction.receiver_id)

         if current_user == sender.id and current_user == receiver.id:
            direction = 'incoming'
         elif current_user == sender.id and current_user != receiver.id: 
            direction = 'outgoing'
         elif current_user == receiver.id:
            direction = 'incoming'

         if not await transactions_service.transaction_id_exists(transaction_id=transaction_id):
            return BadRequest(content=f'Transaction {transaction_id} does not exist.')

         condition_action = transaction.condition
         
         if current_user == sender.id and current_user == receiver.id:
            if condition_action == 'edited':
               new_amount = transaction.amount
               new_category_name = transaction.category_name
               new_receiver_id = transaction.receiver_id
               transaction_edited = await transactions_service.preview_edited_transaction(transaction_id=transaction_id,
                                                                                       new_amount=new_amount,
                                                                                       new_category_name=new_category_name,
                                                                                       new_receiver_id=new_receiver_id)
               transaction_ready = transaction_edited
            elif condition_action == 'sent' and transaction.status == 'pending':
               amount = transaction.amount
               status = 'confirmed'
               transaction_sent = await transactions_service.preview_sent_transaction(transaction_id=transaction_id,
                                                                                amount=amount,
                                                                                status=status,
                                                                                condition_action=condition_action,
                                                                                current_user=current_user)
               transaction_ready = transaction_sent
            elif condition_action == 'cancelled' and transaction.status == 'pending':
               status = 'declined'
               transaction_cancelled = await transactions_service.preview_cancel_transaction(transaction_id=transaction_id, 
                                                                                       status=status,
                                                                                       condition_action=condition_action)
               transaction_ready = transaction_cancelled

         elif current_user == sender.id and current_user != receiver.id:
            if condition_action == 'edited':
               new_amount = transaction.amount
               new_category_name = transaction.category_name
               new_receiver_id = transaction.receiver_id
               transaction_edited = await transactions_service.preview_edited_transaction(transaction_id=transaction_id,
                                                                                    new_amount=new_amount,
                                                                                    new_category_name=new_category_name,
                                                                                    new_receiver_id=new_receiver_id)
               transaction_ready = transaction_edited
            elif condition_action == 'sent' and transaction.status == 'pending':
               amount = transaction.amount
               status = transaction.status
               transaction_sent = await transactions_service.preview_sent_transaction(transaction_id=transaction_id,
                                                                                amount=amount,
                                                                                status=status,
                                                                                condition_action=condition_action,
                                                                                current_user=current_user)
               transaction_ready = transaction_sent
            elif condition_action == 'cancelled' and transaction.status == 'pending':
               status = 'declined'
               transaction_cancelled = await transactions_service.preview_cancel_transaction(transaction_id=transaction_id,
                                                                                       status=status,
                                                                                       condition_action=condition_action)
               transaction_ready = transaction_cancelled

         elif current_user == receiver.id and condition_action == 'sent' and transaction.status == 'confirmed':
            amount = transaction.amount
            status = 'confirmed'
            condition_action = 'sent'
            transaction_confirmed = await transactions_service.preview_confirm_transaction(transaction_id=transaction_id,
                                                                                     amount=amount,
                                                                                     status=status,
                                                                                     condition_action=condition_action,
                                                                                     current_user=current_user)
            transaction_ready = transaction_confirmed

         elif current_user == receiver.id and condition_action == 'sent' and transaction.status == 'declined':
            amount = transaction.amount
            status = 'declined'
            condition_action = 'cancelled'
            transaction_declined = await transactions_service.preview_decline_transaction(transaction_id=transaction_id,
                                                                                    amount=amount,
                                                                                    status=status,
                                                                                    condition_action=condition_action,
                                                                                    current_user=current_user)
            transaction_ready = transaction_declined
         
         transaction_view = [TransactionView.transaction_view(transaction=transaction_ready,
                                                              sender=sender,
                                                              receiver=receiver,
                                                              direction=direction)]

         return transaction_view
      
      else:
         return NotFound(content=f'The transaction you are looking for is not available.')
   
   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Your session has expired. Please log in again to continue using the application.')