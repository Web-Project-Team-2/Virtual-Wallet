from fastapi import APIRouter, Depends, Query
from common.responses import NotFound, BadRequest
from common.authorization import get_current_user
from data.models.recurring_transactions import RecurringTransaction
from schemas.recurring_transactions import RecurringTransactionViewAll, RecurringTransactionView
from services import recurring_transactions_service, user_services, categories_service, cards_services
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

    users_recurring_transactions = await recurring_transactions_service.view_all_recurring_transactions(current_user=current_user,
                                                                                                        recurring_transaction_date=recurring_transaction_date,
                                                                                                        categories_id=categories_id)

    if users_recurring_transactions != [] or users_recurring_transactions != None:
        recurring_transactions_view = []
        for users_recurring_transaction in users_recurring_transactions:
            sender = await user_services.get_user_by_id(user_id=users_recurring_transaction.sender_id)
            receiver = await user_services.get_user_by_id(user_id=users_recurring_transaction.receiver_id)
            category_name = await categories_service.get_category_by_id(category_id=users_recurring_transaction.categories_id)

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
            return recurring_transactions_service.sort_recurring_transactions(recurring_transactions=recurring_transactions_view,
                                                                            reverse=sort == 'desc',
                                                                            attribute=sort_by)
        else:
            return recurring_transactions_view
    
    else:
        return NotFound(content=f'The required recurring transactions you are looking for are not available.')
    

@recurring_transactions_router.get(path='/id/{recurring_transaction_id}', response_model=List[RecurringTransactionView], status_code=201, tags=['Recurrung transactions']) 
async def get_transactions_by_id(recurring_transaction_id: int,
                                 current_user: int = Depends(dependency=get_current_user)):
    '''
    This function returns a more detailed information about a user's specific recurring transaction.\n
    Parameters:\n
    - transaction_id : int\n
        - The ID of the transaction to retrieve details for.\n
    - current_user : int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''

    if await recurring_transactions_service.recurring_transaction_id_exists(recurring_transaction_id=recurring_transaction_id):
        recurring_transaction_view = await recurring_transactions_service.view_recurring_transaction_by_id(recurring_transaction_id=recurring_transaction_id,
                                                                                                           current_user=current_user)
        sender = await user_services.get_user_by_id(user_id=recurring_transaction_view.sender_id)
        receiver = await user_services.get_user_by_id(user_id=recurring_transaction_view.receiver_id)
        category_name = await categories_service.get_category_by_id(category_id=recurring_transaction_view.categories_id)
        
        if not sender or not receiver or not category_name:
            return NotFound(content='Required data not found.')
        
        if recurring_transaction_view.status == 'pending' and recurring_transaction_view.condition == 'edited': 
            message = f'This transaction hasn\'t been sent.'
        if recurring_transaction_view.status == 'confirmed' and recurring_transaction_view.condition == 'sent': 
            message = f'This transaction has been successfully sent.'
        if recurring_transaction_view.status == 'declined' and recurring_transaction_view.condition == 'cancelled': 
            message = f'This transaction has been cancelled.'

        if recurring_transaction_view is None:
            return NotFound(content=f'The recurring transaction you are looking for is not available.')
        else:
            recurring_transaction_view = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=recurring_transaction_view, 
                                                                                              sender=sender, 
                                                                                              receiver=receiver, 
                                                                                              category_name=category_name,
                                                                                              message=message)]
            return recurring_transaction_view
    else:
            return NotFound(content=f'The recurring transaction you are looking for is not available.')


@recurring_transactions_router.post(path='/', status_code=201, tags=['Recurrung transactions']) 
async def create_recurring_transaction(recurring_transaction: RecurringTransaction,
                                       current_user: int = Depends(dependency=get_current_user)):
    '''
    This function makes a recurring transaction to another user and category.\n
    Parameters:\n
    - recurring_transaction : RecurringTransaction\n
        - The recurring transaction's details to be added to the user's recurring transactions.\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''

    sender_id = current_user
    receiver_id = recurring_transaction.receiver_id
    categories_id = recurring_transaction.categories_id

    sender = await user_services.get_user_by_id(user_id=sender_id)
    receiver = await user_services.get_user_by_id(user_id=receiver_id)
    contact = await recurring_transactions_service.contact_id_exists(current_user=current_user,
                                                    reciever_id=recurring_transaction.receiver_id)
    category_name = await categories_service.get_category_by_id(category_id=categories_id)
    receiver_status = await user_services.get_user_by_status(user_id=receiver.id)

    if not sender or not receiver or not contact or not category_name or not receiver_status:
        return NotFound(content='Required data not found. Therefore you cannot continue forward.')
    
    user_status = await user_services.get_user_by_status(user_id=current_user)
    if user_status == 'blocked':
        return BadRequest(content=f'You have been blocked. Therefore the current option is not available for you.')
    
    card_id = await cards_services.get_card_by_user_id(cards_user_id=current_user)
    cards_balance = await cards_services.get_card_info_by_id(card_id=card_id)
    cards_balance = cards_balance.balance
    if cards_balance <= 0:
        return BadRequest(content=f'Your card\'s balance is lower than 0. Therefore the current option is not available for you.')

    if not recurring_transaction.recurring_transaction_date:
        recurring_transaction.recurring_transaction_date = datetime.now()
    if not recurring_transaction.next_payment:
        recurring_transaction.next_payment = datetime.now() + timedelta(days=30)
    if not recurring_transaction.status:
        recurring_transaction.status = 'pending'
    if not recurring_transaction.condition:
        recurring_transaction.condition = 'edited'
    
    if contact == True and receiver_status != 'pending' and receiver_status != 'blocked':
        recurring_transaction_create = await recurring_transactions_service.create_recurring_transaction(recurring_transaction=recurring_transaction)
    else:
        return BadRequest(content=f'The contact is not available. Please, add them to you contacts list first.')

    if recurring_transaction_create is not None: 
        message = f'Recurring transaction successfully created.'
    else:
        return BadRequest(content=f'Recurring transaction creation has failed.')
    
    recurring_transaction_create = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=recurring_transaction_create,
                                                                    sender=sender,
                                                                    receiver=receiver,
                                                                    category_name=category_name,
                                                                    message=message)]

    return recurring_transaction_create


@recurring_transactions_router.put(path='/preview/id/{recurring_transaction_id}', status_code=201, tags=['Recurrung transactions'])  
async def preview_recurring_transaction(recurring_transaction_id: int,
                                        recurring_transaction: RecurringTransaction,
                                        current_user: int = Depends(dependency=get_current_user)):
    '''
    This function preview a recurring transaction and determines if it will be edited, sent, cancelled, confirmed or declined.\n
    Parameters:\n
    - recurring_transaction_id : int\n
        - The ID of the recurring transaction to retrieve details for.\n
    - recurring_transaction : RecurringTransaction\n
        - The recurring transaction's details which will be manipulated.\n
    - current_user : int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''
    
    if await recurring_transactions_service.recurring_transaction_id_exists(recurring_transaction_id=recurring_transaction_id):
        sender = await user_services.get_user_by_id(user_id=recurring_transaction.sender_id)
        receiver = await user_services.get_user_by_id(user_id=recurring_transaction.receiver_id)
        category = await categories_service.get_category_by_id(category_id=recurring_transaction.categories_id)

        condition_action = recurring_transaction.condition
        category_name = category.name

        if recurring_transaction.status == 'pending' and recurring_transaction.condition == 'edited': 
            message = f'This transaction hasn\'t been sent.'
        if recurring_transaction.status == 'confirmed' and recurring_transaction.condition == 'sent': 
            message = f'This transaction has been successfully sent.'
        if recurring_transaction.status == 'declined' and recurring_transaction.condition == 'cancelled': 
            message = f'This transaction has been cancelled.'

        if current_user == sender.id and current_user != receiver.id:
            if condition_action == 'edited':
                new_next_payment = recurring_transaction.next_payment
                new_amount = recurring_transaction.amount
                new_categories_id = recurring_transaction.categories_id
                new_receiver_id = recurring_transaction.receiver_id
                recurring_transaction_edited = await recurring_transactions_service.preview_edited_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                                         new_next_payment=new_next_payment,
                                                                                                                         new_amount=new_amount,
                                                                                                                         new_categories_id=new_categories_id,
                                                                                                                         new_receiver_id=new_receiver_id )
                if recurring_transaction_edited is not None: 
                    message = f'The recurring transaction has been successfully edited.'
                else:
                    return BadRequest(content=f'Recurring transaction editing has failed.')
                recurring_transaction_ready = recurring_transaction_edited
            elif condition_action == 'sent' and recurring_transaction.status == 'pending':
                amount = recurring_transaction.amount
                status = recurring_transaction.status
                recurring_transaction_sent = await recurring_transactions_service.preview_sent_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                                     amount=amount,
                                                                                                                     status=status,
                                                                                                                     condition_action=condition_action,
                                                                                                                     current_user=current_user)
                if recurring_transaction_sent is not None: 
                    message = f'The recurring transaction has been successfully sent.'
                else:
                    return BadRequest(content=f'Recurring transaction sending has failed.')
                recurring_transaction_ready = recurring_transaction_sent
            elif condition_action == 'cancelled' and recurring_transaction.status == 'pending':
                status = 'declined'
                recurring_transaction_cancelled = await recurring_transactions_service.preview_cancelled_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                                               status=status,
                                                                                                                               condition_action=condition_action)
                if recurring_transaction_cancelled is not None: 
                    message = f'The recurring transaction has been cancelled.'
                else:
                    return BadRequest(content=f'Recurring transaction cancelling has failed.')
                recurring_transaction_ready = recurring_transaction_cancelled

        elif current_user == receiver.id and condition_action == 'sent' and recurring_transaction.status == 'confirmed':
            amount = recurring_transaction.amount
            status = 'confirmed'
            condition_action = 'sent'
            recurring_transaction_confirmed = await recurring_transactions_service.preview_confirmed_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                                           amount=amount,
                                                                                                                           status=status,
                                                                                                                           condition_action=condition_action,
                                                                                                                           current_user=current_user)
            if recurring_transaction_confirmed is not None: 
                message = f'The recurring transaction has been successfully confirmed.'
            else:
                return BadRequest(content=f'Recurring transaction confirming has failed.')
            recurring_transaction_ready = recurring_transaction_confirmed
            
        elif current_user == receiver.id and condition_action == 'sent' and recurring_transaction.status == 'declined':
            amount = recurring_transaction.amount
            status = 'declined'
            condition_action = 'cancelled'
            recurring_transaction_declined = await recurring_transactions_service.preview_declined_recurring_transaction(recurring_transaction_id=recurring_transaction_id,
                                                                                                                         amount=amount,
                                                                                                                         status=status,
                                                                                                                         condition_action=condition_action,
                                                                                                                         current_user=current_user)
            if recurring_transaction_declined is not None: 
                message = f'The recurrign transaction has been declined.'
            else:
                return BadRequest(content=f'Recurring transaction declining has failed.')
            recurring_transaction_ready = recurring_transaction_declined
    
        recurring_transaction_view = [RecurringTransactionView.recurring_transaction_view(recurring_transaction=recurring_transaction_ready,
                                                                                          sender=sender,
                                                                                          receiver=receiver,
                                                                                          category_name=category_name,
                                                                                          message=message)]

        return recurring_transaction_view
    
    else:
        return NotFound(content=f'The recurring transaction you are looking for is not available.')