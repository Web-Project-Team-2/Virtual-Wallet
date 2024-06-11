import unittest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status
from schemas.transactions import TransactionFilters
from routers.admin import (
    get_all_users,
    block_user,
    unblock_user,
    approve_user,
    get_user_transactions_,
    deny_user_pending_transactions
)


class TestAdminRouter(unittest.IsolatedAsyncioTestCase):

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('routers.admin.admin_services.get_all_users', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_get_all_users_successful(self, mock_get_current_user, mock_get_all_users, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = False
        mock_get_all_users.return_value = 'all_users'

        result = await get_all_users(current_user=1)
        self.assertEqual(result, 'all_users')

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_get_all_users_not_admin(self, mock_get_current_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = True

        with self.assertRaises(HTTPException) as context:
            await get_all_users(current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "You don't have admin permissions")

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('routers.admin.admin_services.block_user', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_block_user_successful(self, mock_get_current_user, mock_block_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = False
        mock_block_user.return_value = 'user_blocked'

        result = await block_user(user_id=2, current_user=1)
        self.assertEqual(result, 'user_blocked')

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_block_user_not_admin(self, mock_get_current_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = True

        with self.assertRaises(HTTPException) as context:
            await block_user(user_id=2, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "You don't have admin permissions")

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('routers.admin.admin_services.unblock_user', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_unblock_user_successful(self, mock_get_current_user, mock_unblock_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = False
        mock_unblock_user.return_value = 'user_unblocked'

        result = await unblock_user(user_id=2, current_user=1)
        self.assertEqual(result, 'user_unblocked')

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_unblock_user_not_admin(self, mock_get_current_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = True

        with self.assertRaises(HTTPException) as context:
            await unblock_user(user_id=2, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "You don't have admin permissions")

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('routers.admin.admin_services.approve_user', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_approve_user_successful(self, mock_get_current_user, mock_approve_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = False
        mock_approve_user.return_value = 'user_approved'

        result = await approve_user(email='test@test.com', current_user=1)
        self.assertEqual(result, 'user_approved')

    @patch('routers.admin.admin_services.check_if_not_admin', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_approve_user_not_admin(self, mock_get_current_user, mock_check_if_not_admin):
        mock_get_current_user.return_value = 1
        mock_check_if_not_admin.return_value = True

        with self.assertRaises(HTTPException) as context:
            await approve_user(email='test@test.com', current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "You don't have admin permissions")



    @patch('routers.admin.view_user_transactions', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_get_user_transactions_error(self, mock_get_current_user, mock_view_user_transactions):
        mock_get_current_user.return_value = 1
        mock_view_user_transactions.return_value = 'Not authorized'
        filters = TransactionFilters()

        with self.assertRaises(HTTPException) as context:
            await get_user_transactions_(user_id=2, current_user=1, filters=filters)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, 'Not authorized')


    @patch('routers.admin.pending_transactions', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_deny_user_pending_transactions_error(self, mock_get_current_user, mock_pending_transactions):
        mock_get_current_user.return_value = 1
        mock_pending_transactions.return_value = 'Error occurred'

        with self.assertRaises(HTTPException) as context:
            await deny_user_pending_transactions(user_id=2, current_user=1)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Error occurred')



