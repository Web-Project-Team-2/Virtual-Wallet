import unittest
from unittest.mock import patch, AsyncMock
from services.admin_services import *
from schemas.user import AdminUserInfo
from schemas.transactions import TransactionFilters


class TestAdminServices(unittest.IsolatedAsyncioTestCase):

    @patch('services.admin_services.read_query', new_callable=AsyncMock)
    async def test_get_all_users_return_list_of_users(self, mock_read_query):
        mock_read_query.return_value = [
            (1, "daniii", "dani@abv.bg", "0887898991", False, "2024-06-06 11:36:53.231564", 'active', 100.0)
        ]

        result = await get_all_users()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], AdminUserInfo)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].username, "daniii")

    @patch('services.admin_services.update_query', new_callable=AsyncMock)
    async def test_block_user(self, mock_update_query):
        mock_update_query.return_value = True
        result = await block_user(1)
        self.assertTrue(result)

    @patch('services.admin_services.update_query', new_callable=AsyncMock)
    async def test_unblock_user(self, mock_update_query):
        mock_update_query.return_value = True
        result = await unblock_user(1)
        self.assertTrue(result)

    @patch('services.admin_services.update_query', new_callable=AsyncMock)
    async def test_approve_user(self, mock_update_query):
        mock_update_query.return_value = True
        result = await approve_user("dani@abv.bg")
        self.assertTrue(result)

    @patch('services.admin_services.read_query', new_callable=AsyncMock)
    async def test_check_if_not_admin(self, mock_read_query):
        mock_read_query.return_value = [(0,)]
        result = await check_if_not_admin(1)
        self.assertTrue(result)

    @patch('services.admin_services.read_query', new_callable=AsyncMock)
    async def test_view_user_transactions(self, mock_read_query):
        mock_read_query.side_effect = [
            [(True,)],  # Admin status check
            [("completed", "2024-06-06 11:36:53.231564", 100.0, 1, 2, 3)]
        ]

        filters = TransactionFilters(
            start_date=None,
            end_date=None,
            sender_id=None,
            recipient_id=None,
            direction=None,
            sort_by='transaction_date',
            sort_order='DESC',
            limit=10,
            offset=0
        )

        result = await view_user_transactions(1, 1, filters)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['status'], "completed")
        self.assertEqual(result[0]['transaction_date'], "2024-06-06 11:36:53.231564")
        self.assertEqual(result[0]['amount'], 100.0)
        self.assertEqual(result[0]['sender_id'], 1)
        self.assertEqual(result[0]['receiver_id'], 2)
        self.assertEqual(result[0]['card_id'], 3)

    @patch('services.admin_services.read_query', new_callable=AsyncMock)
    @patch('services.admin_services.update_query', new_callable=AsyncMock)
    async def test_pending_transactions(self, mock_update_query, mock_read_query):
        mock_read_query.side_effect = [
            [(True,)],  # Admin status check
            [(1, 100.0)]  # Pending transactions
        ]
        mock_update_query.return_value = True

        result = await pending_transactions(1, 1)
        self.assertEqual(result, "All pending transactions have been declined.")


if __name__ == '__main__':
    unittest.main()
