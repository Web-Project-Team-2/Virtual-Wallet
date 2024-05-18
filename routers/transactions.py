from fastapi import APIRouter
from common.responses import NotFound, BadRequest, InternalServerError, Unauthorized, NoContent
from data.models.transactions import Transaction
from schemas import transactions
from services import transactions_service
from datetime import datetime, timedelta

# Add money to wallet - to transfer money between own credit/debit, MUST - in progress
# Make transaction  - to transfer money to other users, MUST - in progress
# Approve/decline transaction  - to confirm, deny transactions. MUST - need help
# List transactions - view their transactions. MUST - in progress
# Filter by date, sender, recipient, and direction (in/out)  
# Sort by date or amount  
# Withdraw  


transactions_router = APIRouter(prefix='/transactions')


@transactions_router.get('/user_id/{sender_id}')  
def get_transactions(sender_id: int):
     '''Shows a list of all the user's transactions.\n
     Parameters explanation to follow.
     '''

     transactions_lst = transactions_service.show_all_transactions(sender_id)

     return transactions_lst 



@transactions_router.get('/id/{transaction_id}') 
def get_transactions_by_id():
     '''Shows more detailed information about a user's transactions.\n
     Parameters explanation to follow.
     '''
     pass

@transactions_router.post('/wallet', status_code=201) 
def add_money_to_wallet():
     '''Makes a transaction to the wallet's ballance.\n
     Parameters explanation to follow.
     '''
     pass

@transactions_router.post('/', status_code=201) 
def make_a_transaction():
     '''Makes a transaction to another user or category.\n
     Parameters explanation to follow.
     '''
     pass

# @transactions_router.put('/approval', status_code=201) # POST or PUT? 
# def approve_a_transaction():
#      '''Makes a transaction to another user or category.\n
#      Parameters explanation to follow.
#      '''
#      pass


