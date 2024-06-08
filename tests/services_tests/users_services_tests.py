import unittest
from unittest.mock import patch, AsyncMock
from services.user_services import create, find_by_email, try_login, User, IntegrityError

ID = 1
EMAIL = 'test@test.bg'
USERNAME = 'test'
PASSWORD = 'testpassword'  # At least 8 characters
PHONE = '1234567890'
IS_ADMIN = False
CREATE_AT = '2023-01-01'
STATUS = 'active'
BALANCE = 0.0


class TestWalletServices(unittest.IsolatedAsyncioTestCase):
    @patch('services.user_services.insert_query', new_callable=AsyncMock)
    @patch('services.user_services.read_query', new_callable=AsyncMock)
    async def test_create_user_correctly(self, mock_read_query, mock_insert_query):
        mock_id = 1
        mock_insert_query.return_value = mock_id
        mock_read_query.return_value = [(ID, EMAIL, USERNAME, PASSWORD, PHONE, IS_ADMIN, CREATE_AT, STATUS, BALANCE)]

        result = await create(USERNAME, PASSWORD, EMAIL, PHONE)

        self.assertIsInstance(result, User)
        self.assertEqual(result.id, mock_id)
        self.assertEqual(result.username, USERNAME)
        self.assertEqual(result.password, PASSWORD)

    @patch('services.user_services.insert_query', new_callable=AsyncMock)
    async def test_create_user_failed(self, mock_insert_query):
        mock_insert_query.side_effect = IntegrityError

        result = await create(USERNAME, PASSWORD, EMAIL, PHONE)

        self.assertIsNone(result)

    @patch('services.user_services.read_query', new_callable=AsyncMock)
    async def test_find_by_email_correctly(self, mock_read_query):
        mock_read_query.return_value = [(ID, EMAIL, USERNAME, PASSWORD, PHONE, IS_ADMIN, CREATE_AT, STATUS, BALANCE)]

        result = await find_by_email(EMAIL)

        self.assertIsInstance(result, User)
        self.assertEqual(result.id, ID)
        self.assertEqual(result.email, EMAIL)
        self.assertEqual(result.username, USERNAME)
        self.assertEqual(result.password, PASSWORD)

    @patch('services.user_services.read_query', new_callable=AsyncMock)
    async def test_find_by_email_failed(self, mock_read_query):
        mock_read_query.side_effect = None

        result = await find_by_email(EMAIL)

        self.assertIsNone(result)

    async def test_try_login_correctly(self):
        with patch('services.user_services.find_by_email', new_callable=AsyncMock) as mock_find_by_email, \
             patch('security.password_hashing.verify_password', new_callable=AsyncMock) as mock_verify_password:
            mock_find_by_email.return_value = User(id=ID, email=EMAIL, username=USERNAME, password=PASSWORD, phone_number=PHONE, is_admin=IS_ADMIN, create_at=CREATE_AT, status=STATUS, balance=BALANCE)
            mock_verify_password.return_value = True

            result = await try_login(EMAIL, PASSWORD)

            self.assertIsInstance(result, User)
            self.assertEqual(result.id, ID)
            self.assertEqual(result.email, EMAIL)
            self.assertEqual(result.username, USERNAME)
            self.assertEqual(result.password, PASSWORD)


    @patch('services.user_services.find_by_email', new_callable=AsyncMock)
    @patch('security.password_hashing.verify_password', new_callable=AsyncMock)
    async def test_try_login_failed_when_find_by_email_is_None(self, mock_verify_password, mock_find_by_email):
        mock_find_by_email.return_value = None
        mock_verify_password.return_value = True

        result = await try_login(EMAIL, PASSWORD)

        self.assertIsNone(result)

    @patch('services.user_services.find_by_email', new_callable=AsyncMock)
    @patch('security.password_hashing.verify_password', new_callable=AsyncMock)
    async def test_try_login_failed_when_both_are_None(self, mock_verify_password, mock_find_by_email):
        mock_find_by_email.return_value = None
        mock_verify_password.return_value = False

        result = await try_login(EMAIL, PASSWORD)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
