from fastapi import APIRouter, Depends, HTTPException, status, Query
from jose import JWTError
from common.responses import NotFound, BadRequest
from common.authorization import get_current_user
from data.models.recurring_transactions import RecurringTransaction
from schemas.recurring_transactions import RecurringTransactionViewAll, RecurringTransactionView
from services import recurring_transactions_service
from datetime import datetime, timedelta
from typing import List


recurring_transactions_router = APIRouter(prefix='/api/recurring_transactions')


@recurring_transactions_router.get(path='/', response_model=List[RecurringTransactionViewAll], status_code=201, tags=['Recurrung transactions'])  
async def get_users_recurring_transactions(sort: str | None = None, 
                                     sort_by: str | None = None,
                                     page: int = Query(default=None, gt=0),
                                     recurring_transactions_per_page: int = Query(default=5, gt=0),
                                     recurring_transaction_date: str | None = None,
                                     categories_id: int | None = None,
                                     current_user: int = Depends(dependency=get_current_user)):
    '''
    This function returns a list of all the recurring transactions for the specified user - they are always 'outgoing'.\n
    It allows users to retrieve their recurring transactions with optional sorting, pagination, and filtering by date and category.\n
    Parameters:\n
    - sort: str | None\n
        - The sort order of the transactions. Acceptable values are 'asc' for ascending or 'desc' for descending.\n
    - sort_by: str | None\n
        - The attributes to sort the transactions are 'transaction_date' and 'amount'.\n
    - page: int | None\n
        - The page number to retrieve, for paginated results. Must be greater than 0. If not specified, all transactions are returned.\n
    - recurring_transactions_per_page: int\n
        - The number of recurring transactions to retrieve per page. Default is 5, must be greater than 0.\n  
    - recurring_transaction_date: str | None\n
        - Filter recurring transactions by a specific date.\n
    - categories_id: int | None\n
        - Filter recurring transactions by a specific category ID.\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''
    try:
        users_recurring_transactions = await recurring_transactions_service.view_all_recurring_transactions(current_user=current_user,
                                                                                                      recurring_transaction_date=recurring_transaction_date,
                                                                                                      categories_id=categories_id)

        recurring_transactions_view = []
        for users_recurring_transaction in users_recurring_transactions:
            sender = await recurring_transactions_service.get_user_by_id(user_id=users_recurring_transaction.sender_id)
            receiver = await recurring_transactions_service.get_user_by_id(user_id=users_recurring_transaction.receiver_id)
            category_name = await recurring_transactions_service.get_category_by_id(category_id=users_recurring_transaction.categories_id)
            if not sender or not receiver or not category_name:
                return NotFound(content='Required data not found.')
            recurring_transactions_view.append(RecurringTransactionViewAll.recurring_transactions_view(recurring_transaction=users_recurring_transaction, 
                                                                                                sender=sender,
                                                                                                receiver=receiver, 
                                                                                                category_name=category_name))
        
        if page:
            start = (page - 1) * recurring_transactions_per_page
            end = start + recurring_transactions_per_page
            recurring_transactions_view = recurring_transactions_view[start:end]

        if sort and (sort == 'asc' or sort == 'desc'):
            return await recurring_transactions_service.sort_recurring_transactions(recurring_transactions=recurring_transactions_view,
                                                                              reverse=sort == 'desc',
                                                                              attribute=sort_by)
        else:
            return recurring_transactions_view
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Your session has expired. Please log in again to continue using the application.')


@recurring_transactions_router.get(path='/id/{recurring_transaction_id}', response_model=List[RecurringTransactionView], status_code=201, tags=['Recurrung transactions']) 
async def get_transactions_by_id(recurring_transaction_id: int, current_user: int = Depends(dependency=get_current_user)):
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
        recurring_transaction_view = await recurring_transactions_service.view_recurring_transaction_by_id(recurring_transaction_id=recurring_transaction_id,
                                                                                                     current_user=current_user)
        sender = await recurring_transactions_service.get_user_by_id(user_id=recurring_transaction_view.sender_id)
        receiver = await recurring_transactions_service.get_user_by_id(user_id=recurring_transaction_view.receiver_id)
        category_name = await recurring_transactions_service.get_category_by_id(category_id=recurring_transaction_view.categories_id)
        
        if not sender or not receiver:
            return NotFound(content='Required data not found.')
      
        if recurring_transaction_view is None:
            return NotFound(content=f'The transaction you are looking for is not available.')
        else:
            recurring_transaction_view = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=recurring_transaction_view, 
                                                                                    sender=sender, 
                                                                                    receiver=receiver, 
                                                                                    category_name=category_name)]
            return recurring_transaction_view
      
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Your session has expired. Please log in again to continue using the application.')


@recurring_transactions_router.post(path='/', status_code=201, tags=['Recurrung transactions']) 
async def create_recurring_transaction(recurring_transaction: RecurringTransaction, current_user: int = Depends(dependency=get_current_user)):
    '''
    This function makes a transaction to another user or category.\n
    Parameters:\n
    - recurring_transaction : RecurringTransaction\n
        - The transaction details to be added to the user's recurring transactions.\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''
    try:
        if not recurring_transaction.recurring_transaction_date:
            recurring_transaction.recurring_transaction_date = datetime.now()
        if not recurring_transaction.next_payment:
            recurring_transaction.next_payment = datetime.now() + timedelta(days=30) 

        sender_id = current_user
        receiver_id = recurring_transaction.receiver_id
        categories_id = recurring_transaction.categories_id

        recurring_transaction_create = await recurring_transactions_service.create_recurring_transaction(recurring_transaction=recurring_transaction)
        sender = await recurring_transactions_service.get_user_by_id(user_id=sender_id)
        receiver = await recurring_transactions_service.get_user_by_id(user_id=receiver_id)
        category_name = await recurring_transactions_service.get_category_by_id(category_id=categories_id)

        if not sender or not receiver or not category_name:
            return NotFound(content='Required data not found.')
        
        recurring_transaction_create = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=recurring_transaction_create,
                                                                        sender=sender,
                                                                        receiver=receiver,
                                                                        category_name=category_name)]

        return recurring_transaction_create
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Your session has expired. Please log in again to continue using the application.')


@recurring_transactions_router.put(path='/preview/id/{transaction_id}', status_code=201, tags=['Recurrung transactions'])  
async def preview_recurring_transaction(recurring_transaction_id: int, recurring_transaction: RecurringTransaction, current_user: int = Depends(dependency=get_current_user)):
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
        if await recurring_transactions_service.recurring_transaction_id_exists(recurring_transaction_id=recurring_transaction_id):
            sender = await recurring_transactions_service.get_user_by_id(user_id=recurring_transaction.sender_id)
            receiver = await recurring_transactions_service.get_user_by_id(user_id=recurring_transaction.receiver_id)

            if not await recurring_transactions_service.recurring_transaction_id_exists(recurring_transaction_id=recurring_transaction_id):
                return BadRequest(content=f'The recurring transaction {recurring_transaction_id} does not exist.')

            condition_action = recurring_transaction.condition
        
            if current_user == sender.id and current_user == receiver.id:
                if condition_action == 'edited':
                    new_amount = recurring_transaction.amount
                    new_category_name = recurring_transaction.category_name
                    new_receiver_id = recurring_transaction.receiver_id
                    transaction_edited = await recurring_transactions_service.preview_edited_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                new_amount=new_amount,
                                                                                                new_category_name=new_category_name,
                                                                                                new_receiver_id=new_receiver_id)
                    transaction_ready = transaction_edited
                elif condition_action == 'sent' and recurring_transaction.status == 'pending':
                    amount = recurring_transaction.amount
                    status = 'confirmed'
                    transaction_sent = await recurring_transactions_service.preview_send_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                        amount=amount,
                                                                                                        status=status,
                                                                                                        condition_action=condition_action,
                                                                                                        current_user=current_user)
                    transaction_ready = transaction_sent
                elif condition_action == 'cancelled' and recurring_transaction.status == 'pending':
                    status = 'declined'
                    transaction_cancelled = await recurring_transactions_service.preview_cancel_recurring_transaction(transaction_id=recurring_transaction_id, 
                                                                                                                status=status,
                                                                                                                condition_action=condition_action)
                    transaction_ready = transaction_cancelled

            elif current_user == sender.id and current_user != receiver.id:
                if condition_action == 'edited':
                    new_amount = recurring_transaction.amount
                    new_category_name = recurring_transaction.category_name
                    new_receiver_id = recurring_transaction.receiver_id
                    transaction_edited = await recurring_transactions_service.preview_edited_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                            new_amount=new_amount,
                                                                                                            new_category_name=new_category_name,
                                                                                                            new_receiver_id=new_receiver_id )
                    transaction_ready = transaction_edited
                elif condition_action == 'sent' and recurring_transaction.status == 'pending':
                    amount = recurring_transaction.amount
                    status = recurring_transaction.status
                    transaction_sent = await recurring_transactions_service.preview_send_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                        amount=amount,
                                                                                                        status=status,
                                                                                                        condition_action=condition_action,
                                                                                                        current_user=current_user)
                    transaction_ready = transaction_sent
                elif condition_action == 'cancelled' and recurring_transaction.status == 'pending':
                    status = 'declined'
                    transaction_cancelled = await recurring_transactions_service.preview_cancel_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                                status=status,
                                                                                                                condition_action=condition_action)
                    transaction_ready = transaction_cancelled

            elif current_user == receiver.id and condition_action == 'sent' and recurring_transaction.status == 'confirmed':
                amount = recurring_transaction.amount
                status = 'confirmed'
                condition_action = 'sent'
                transaction_confirmed = await recurring_transactions_service.preview_confirm_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                            amount=amount,
                                                                                                            status=status,
                                                                                                            condition_action=condition_action,
                                                                                                            current_user=current_user)
                transaction_ready = transaction_confirmed
                
            elif current_user == receiver.id and condition_action == 'sent' and recurring_transaction.status == 'declined':
                amount = recurring_transaction.amount
                status = 'declined'
                condition_action = 'cancelled'
                transaction_declined = await recurring_transactions_service.preview_decline_recurring_transaction(transaction_id=recurring_transaction_id,
                                                                                                            amount=amount,
                                                                                                            status=status,
                                                                                                            condition_action=condition_action,
                                                                                                            current_user=current_user)
                transaction_ready = transaction_declined
        
            transaction_view = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=transaction_ready,
                                                                                    sender=sender,
                                                                                    receiver=receiver)]

            return transaction_view
        
        else:
            return NotFound(content=f'The recurring transaction you are looking for is not available.')
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Your session has expired. Please log in again to continue using the application.')