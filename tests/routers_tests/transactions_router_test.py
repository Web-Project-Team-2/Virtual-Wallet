import unittest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from routers.transactions import get_users_transactions
from data.models.transactions import Transaction
from data.models.user import User

class TestTransactionsRouter(unittest.IsolatedAsyncioTestCase):

    @patch('routers.transactions_router.transactions_service.view_all_transactions', new_callable=AsyncMock)
    @patch('routers.transactions_router.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_transactions_successful(self, mock_get_user_by_id, mock_view_all_transactions):
        mock_view_all_transactions.return_value = [
            Transaction(id=1, sender_id=1, receiver_id=2, amount=100, transaction_date='2023-06-01', description='Test transaction'),
            Transaction(id=2, sender_id=2, receiver_id=1, amount=150, transaction_date='2023-06-02', description='Another test transaction')
        ]
        mock_get_user_by_id.side_effect = [
            User(id=1, username='user1', email='user1@example.com'),
            User(id=2, username='user2', email='user2@example.com'),
            User(id=2, username='user2', email='user2@example.com'),
            User(id=1, username='user1', email='user1@example.com')
        ]

        transactions = await get_users_transactions(current_user=1, page=1, transactions_per_page=2)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].transaction.id, 1)
        self.assertEqual(transactions[1].transaction.id, 2)
        self.assertEqual(transactions[0].direction, 'outgoing')
        self.assertEqual(transactions[1].direction, 'incoming')

    @patch('routers.transactions_router.transactions_service.view_all_transactions', new_callable=AsyncMock)
    async def test_get_users_transactions_no_transactions(self, mock_view_all_transactions):
        mock_view_all_transactions.return_value = []

        with self.assertRaises(HTTPException) as context:
            await get_users_transactions(current_user=1)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, 'The required transactions you are looking for are not available.')

    @patch('routers.transactions_router.transactions_service.view_all_transactions', new_callable=AsyncMock)
    @patch('routers.transactions_router.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_transactions_not_found(self, mock_get_user_by_id, mock_view_all_transactions):
        mock_view_all_transactions.return_value = [
            Transaction(id=1, sender_id=1, receiver_id=2, amount=100, transaction_date='2023-06-01', description='Test transaction')
        ]
        mock_get_user_by_id.return_value = None

        with self.assertRaises(HTTPException) as context:
            await get_users_transactions(current_user=1)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, 'Required data not found.')