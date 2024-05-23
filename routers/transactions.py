from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from common.responses import NotFound, BadRequest
from common.authorization import get_current_user
from data.models.transactions import Transaction
from schemas.transactions import TransactionViewAll, TransactionView
from services import transactions_service, user_services, categories_service
from datetime import datetime
from typing import List

# branchtest

transactions_router = APIRouter(prefix='/transactions')

@transactions_router.get('/', response_model=List[TransactionViewAll], status_code=201, tags=['Transactions'])  
def get_users_transactions(current_user: int = Depends(get_current_user)):
   '''
   This function returns a list of all the transactions for the specified user.\n

   Parameters:\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   ''' 
   try:
      users_transactions = transactions_service.view_all_transactions(current_user)
      transactions_view = [TransactionViewAll.transaction_view(transaction) for transaction in users_transactions]
      return transactions_view
   
   except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Your session has expired.'
        )

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
   
   transaction = transactions_service.show_transaction_by_id(transaction_id)

   if transaction is None:
      return NotFound() # status_code=404
   else:
      return transaction

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

   transaction.transaction_date = datetime.now()
   transaction.transaction_date = transaction.transaction_date.strftime("%Y/%m/%d %H:%M")

   return transactions_service.add_money_to_users_ballnace(transaction, current_user)

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

   transaction.receiver_id = user_services.user_id_exists(transaction.receiver_id)
   transaction.categories_id = categories_service.find_category_by_id(transaction.categories_id)

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