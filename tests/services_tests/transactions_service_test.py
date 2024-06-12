import unittest
from unittest.mock import patch, AsyncMock
from services.transactions_service import view_all_transactions, sort_transactions
from data.models.transactions import Transaction
from common.responses import BadRequest

class TestTransactionsService(unittest.IsolatedAsyncioTestCase):

    @patch('services.transactions_service.read_query', new_callable=AsyncMock)
    async def test_view_all_transactions_filter_by_date(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'completed', 'normal', '2024-06-10', 100.0, 'groceries', 1, 2, None),
            (2, 'completed', 'normal', '2024-06-12', 50.0, 'utilities', 1, 3, None)
        ]

        transactions = await view_all_transactions(current_user=1, transaction_date='2024-06-12')

        self.assertEqual(len(transactions), 1)
        self.assertIsInstance(transactions[0], Transaction)
        self.assertEqual(transactions[0].id, 2)

    @patch('services.transactions_service.read_query', new_callable=AsyncMock)
    async def test_view_all_transactions_filter_by_sender(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'completed', 'normal', '2024-06-10', 100.0, 'groceries', 1, 2, None),
            (2, 'completed', 'normal', '2024-06-12', 50.0, 'utilities', 1, 3, None)
        ]

        transactions = await view_all_transactions(current_user=1, sender='2')

        self.assertEqual(len(transactions), 1)
        self.assertIsInstance(transactions[0], Transaction)
        self.assertEqual(transactions[0].id, 1)

    @patch('services.transactions_service.read_query', new_callable=AsyncMock)
    async def test_view_all_transactions_filter_by_receiver(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'completed', 'normal', '2024-06-10', 100.0, 'groceries', 1, 2, None),
            (2, 'completed', 'normal', '2024-06-12', 50.0, 'utilities', 1, 3, None)
        ]

        transactions = await view_all_transactions(current_user=1, receiver='3')

        self.assertEqual(len(transactions), 1)
        self.assertIsInstance(transactions[0], Transaction)
        self.assertEqual(transactions[0].id, 2)

    @patch('services.transactions_service.read_query', new_callable=AsyncMock)
    async def test_view_all_transactions_filter_by_direction(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'completed', 'normal', '2024-06-10', 100.0, 'groceries', 1, 2, None),
            (2, 'completed', 'normal', '2024-06-12', 50.0, 'utilities', 1, 3, None)
        ]

        transactions_incoming = await view_all_transactions(current_user=2, direction='incoming')
        transactions_outgoing = await view_all_transactions(current_user=1, direction='outgoing')

        self.assertEqual(len(transactions_incoming), 1)
        self.assertEqual(transactions_incoming[0].id, 1)
        self.assertEqual(len(transactions_outgoing), 1)
        self.assertEqual(transactions_outgoing[0].id, 2)

    @patch('services.transactions_service.read_query', new_callable=AsyncMock)
    async def test_view_all_transactions_no_filters(self, mock_read_query):
        mock_read_query.return_value = [
            (1, 'completed', 'normal', '2024-06-10', 100.0, 'groceries', 1, 2, None),
            (2, 'completed', 'normal', '2024-06-12', 50.0, 'utilities', 1, 3, None)
        ]

        transactions = await view_all_transactions(current_user=1)

        self.assertEqual(len(transactions), 2)
        self.assertIsInstance(transactions[0], Transaction)
        self.assertEqual(transactions[0].id, 1)
        self.assertEqual(transactions[1].id, 2)

    def test_sort_transactions_by_date(self):
        transactions = [
            Transaction(id=1, transaction_date='2024-06-10', amount=100.0),
            Transaction(id=2, transaction_date='2024-06-12', amount=50.0),
            Transaction(id=3, transaction_date='2024-06-11', amount=75.0)
        ]

        sorted_transactions = sort_transactions(transactions, attribute='transaction_date')

        self.assertEqual(sorted_transactions[0].id, 1)
        self.assertEqual(sorted_transactions[1].id, 3)
        self.assertEqual(sorted_transactions[2].id, 2)

    def test_sort_transactions_by_amount(self):
        transactions = [
            Transaction(id=1, transaction_date='2024-06-10', amount=100.0),
            Transaction(id=2, transaction_date='2024-06-12', amount=50.0),
            Transaction(id=3, transaction_date='2024-06-11', amount=75.0)
        ]

        sorted_transactions = sort_transactions(transactions, attribute='amount')

        self.assertEqual(sorted_transactions[0].id, 2)
        self.assertEqual(sorted_transactions[1].id, 3)
        self.assertEqual(sorted_transactions[2].id, 1)

    def test_sort_transactions_invalid_attribute(self):
        transactions = [
            Transaction(id=1, transaction_date='2024-06-10', amount=100.0),
            Transaction(id=2, transaction_date='2024-06-12', amount=50.0),
            Transaction(id=3, transaction_date='2024-06-11', amount=75.0)
        ]

        with self.assertRaises(BadRequest):
            sort_transactions(transactions, attribute='invalid')

if __name__ == '__main__':
    unittest.main()
