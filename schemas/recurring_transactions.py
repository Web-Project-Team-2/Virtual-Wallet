from pydantic import BaseModel


class RecurringTransactionViewAll(BaseModel):
    recurring_transaction_date: str
    next_payment: str
    amount: float
    sender: str
    receiver: str
    category_name: str

    @classmethod
    def recurring_transactions_view(cls, recurring_transaction, sender, receiver, category_name):
        return cls(
            recurring_transaction_date=recurring_transaction.recurring_transaction_date.strftime('%Y/%m/%d %H:%M'),
            next_payment=recurring_transaction.next_payment.strftime('%Y/%m/%d %H:%M'),
            amount=recurring_transaction.amount,
            sender=sender.username,
            receiver=receiver.username,
            category_name=category_name.name
        )


class RecurringTransactionView(BaseModel):
    status: str 
    condition: str 
    recurring_transaction_date: str
    next_payment: str
    amount: float
    category_name: str
    sender: str 
    receiver: str
    direction: str = 'outgoing'
    message: str

    @classmethod
    def recurring_transaction_view(cls, recurring_transaction, sender, receiver, category_name, message):
       
        return cls(
            status=recurring_transaction.status,
            condition=recurring_transaction.condition,
            recurring_transaction_date=recurring_transaction.recurring_transaction_date.strftime('%Y/%m/%d %H:%M'),
            next_payment=recurring_transaction.next_payment.strftime('%Y/%m/%d %H:%M'),
            amount=recurring_transaction.amount,
            category_name=category_name,
            sender=sender.username,
            receiver=receiver.username,
            direction='outgoing',
            message=message
        )