from fastapi import APIRouter, Depends, HTTPException, status, Query
from jose import JWTError
from common.responses import BadRequest, NotFound
from common.authorization import get_current_user
from data.models.recurring_transactions import RecurrringTransaction
from schemas.transactions import TransactionViewAll, TransactionView
from services import transactions_service, recurring_transactions_service
from datetime import datetime
from typing import List


recurring_transactions_router = APIRouter(prefix='/api/recurring_transactions')


@recurring_transactions_router.get('/', response_model=List[TransactionViewAll], status_code=201, tags=['Recurrung transactions'])  
def get_users_recurring_transactions():
    pass


@recurring_transactions_router.get('/id/{recurring_transaction_id}', response_model=List[TransactionView], status_code=201, tags=['Recurrung transactions']) 
def get_transactions_by_id():
    pass

@recurring_transactions_router.post('/', status_code=201, tags=['Recurrung transactions']) 
def make_a_transaction():
    pass

@recurring_transactions_router.put('/approval/id/{transaction_id}', status_code=201, tags=['Recurrung transactions'])  
def approve_a_transaction():
    pass