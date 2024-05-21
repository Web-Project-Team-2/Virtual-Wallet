from fastapi import APIRouter, Depends, status, HTTPException
from common.responses import NotFound, BadRequest, InternalServerError, Unauthorized, NoContent
from common.authorization import get_current_user
from data.models.transactions import Transaction
from schemas import transactions
from services import transactions_service
from datetime import datetime, timedelta

transactions_router = APIRouter(prefix='/transactions')

@transactions_router.get('/', status_code=201, tags=['Transactions'])  
def get_users_transactions(current_user: int = Depends(get_current_user)):
     '''
     This function returns a list of all the transactions for the specified user.\n
     
     Parameters:\n
     - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
     '''

     # if not current_user:
     #      return BadRequest(content=f'You currently have no access to this section, please login.') 

     transactions_lst = transactions_service.show_all_transactions(current_user)

     return transactions_lst 

@transactions_router.get('/id/{transaction_id}', status_code=201, tags=['Transactions']) 
def get_transactions_by_id(transaction_id: int, current_user: int = Depends(get_current_user)):
     '''
     This finction returns a more detailed information about a user's transactions.\n

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

     return transactions_service.create_transactions(transaction, current_user)

@transactions_router.post('/', status_code=201, tags=['Transactions']) 
def make_a_transaction():
     '''
     Makes a transaction to another user or category.\n
     Parameters explanation to follow.
     '''
     pass

@transactions_router.put('/approval', status_code=201, tags=['Transactions'])  
def approve_a_transaction():
     '''
     Confirmes or declines a transaction.\n
     Parameters explanation to follow.
     '''
     pass