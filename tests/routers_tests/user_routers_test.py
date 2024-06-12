import unittest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status
from schemas.user import UserCreate, UserLogin, UserInfoUpdate, UserOut
from schemas.contacts import ContactCreate
from schemas.deposit import Deposit
from schemas.withdraw import WithdrawMoney
from routers.users import register, login, view_credit_info, view_user_info, create_contact, delete_contact, get_all_contacts, update_user_info, deposit, withdraw

class TestUsersRouter(unittest.IsolatedAsyncioTestCase):


    @patch('routers.users.user_services.try_login', new_callable=AsyncMock)
    async def test_login_successful(self, mock_try_login):
        mock_try_login.return_value = AsyncMock(id=1)
        user_credentials = UserLogin(email='test@test.com', password='password')
        result = await login(user_credentials)
        self.assertIn('access_token', result)

    @patch('routers.users.user_services.try_login', new_callable=AsyncMock)
    async def test_login_invalid_credentials(self, mock_try_login):
        mock_try_login.return_value = None
        user_credentials = UserLogin(email='test@test.com', password='wrongpassword')

        with self.assertRaises(HTTPException) as context:
            await login(user_credentials)
        self.assertEqual(context.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(context.exception.detail, "Invalid Credentials")

    @patch('routers.users.user_services.view', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_view_credit_info_successful(self, mock_get_current_user, mock_view):
        mock_get_current_user.return_value = 1
        mock_view.return_value = 'credit_info'
        result = await view_credit_info(current_user=1)
        self.assertEqual(result, 'credit_info')

    @patch('routers.users.user_services.view', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_view_credit_info_error(self, mock_get_current_user, mock_view):
        mock_get_current_user.return_value = 1
        mock_view.side_effect = Exception
        with self.assertRaises(HTTPException) as context:
            await view_credit_info(current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to show credit information")

    @patch('routers.users.user_services.view_profile', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_view_user_info_successful(self, mock_get_current_user, mock_view_profile):
        mock_get_current_user.return_value = 1
        mock_view_profile.return_value = 'user_info'
        result = await view_user_info(current_user=1)
        self.assertEqual(result, 'user_info')

    @patch('routers.users.user_services.view_profile', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_view_user_info_error(self, mock_get_current_user, mock_view_profile):
        mock_get_current_user.return_value = 1
        mock_view_profile.side_effect = Exception
        with self.assertRaises(HTTPException) as context:
            await view_user_info(current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to show user information")

    @patch('routers.users.user_services.create_contact', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_create_contact_successful(self, mock_get_current_user, mock_create_contact):
        mock_get_current_user.return_value = 1
        mock_create_contact.return_value = {'contact_username': 'contactuser'}
        contact_create = ContactCreate(contact_user_id=2)
        result = await create_contact(contact_create, current_user=1)
        self.assertEqual(result, {"message": "Contact created successfully", "contact_username": "contactuser"})

    @patch('routers.users.user_services.create_contact', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_create_contact_error(self, mock_get_current_user, mock_create_contact):
        mock_get_current_user.return_value = 1
        mock_create_contact.return_value = None
        contact_create = ContactCreate(contact_user_id=2)
        with self.assertRaises(HTTPException) as context:
            await create_contact(contact_create, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to create contact. The user might already be a contact or does not exist.")

    @patch('routers.users.user_services.delete_contact', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_delete_contact_successful(self, mock_get_current_user, mock_delete_contact):
        mock_get_current_user.return_value = 1
        mock_delete_contact.return_value = True
        result = await delete_contact(2, current_user=1)
        self.assertEqual(result, {"message": "Contact deleted successfully"})

    @patch('routers.users.user_services.delete_contact', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_delete_contact_error(self, mock_get_current_user, mock_delete_contact):
        mock_get_current_user.return_value = 1
        mock_delete_contact.return_value = False
        with self.assertRaises(HTTPException) as context:
            await delete_contact(2, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to delete contact. The contact does not exist.")

    @patch('routers.users.user_services.get_all_contacts', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_get_all_contacts_successful(self, mock_get_current_user, mock_get_all_contacts):
        mock_get_current_user.return_value = 1
        mock_get_all_contacts.return_value = ['contact1', 'contact2']
        result = await get_all_contacts(current_user=1)
        self.assertEqual(result, {"contacts": ['contact1', 'contact2']})

    @patch('routers.users.user_services.get_all_contacts', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_get_all_contacts_error(self, mock_get_current_user, mock_get_all_contacts):
        mock_get_current_user.return_value = 1
        mock_get_all_contacts.return_value = None
        with self.assertRaises(HTTPException) as context:
            await get_all_contacts(current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to fetch contacts.")






    @patch('routers.users.user_services.deposit_money', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_deposit_error(self, mock_get_current_user, mock_deposit_money):
        mock_get_current_user.return_value = 1
        mock_deposit_money.side_effect = Exception
        money = Deposit(deposit_money=100.0)
        with self.assertRaises(HTTPException) as context:
            await deposit(money, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to deposit money.")

    @patch('routers.users.user_services.withdraw_money', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_withdraw_successful(self, mock_get_current_user, mock_withdraw_money):
        mock_get_current_user.return_value = 1
        mock_withdraw_money.return_value = 'withdraw_successful'
        money = WithdrawMoney(withdraw_money=50.0)
        result = await withdraw(money, current_user=1)
        self.assertEqual(result, 'withdraw_successful')

    @patch('routers.users.user_services.withdraw_money', new_callable=AsyncMock)
    @patch('common.authorization.get_current_user', new_callable=AsyncMock)
    async def test_withdraw_error(self, mock_get_current_user, mock_withdraw_money):
        mock_get_current_user.return_value = 1
        mock_withdraw_money.side_effect = Exception
        money = WithdrawMoney(withdraw_money=50.0)
        with self.assertRaises(HTTPException) as context:
            await withdraw(money, current_user=1)
        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(context.exception.detail, "Unable to withdraw money.")

