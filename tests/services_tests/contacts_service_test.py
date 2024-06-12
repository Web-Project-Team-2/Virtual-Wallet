from data.models.contacts import Contact
from services.contacts_service import view_all_contacts, view_contact_by_id, create_contact, contact_id_exists
import unittest
from unittest.mock import patch, AsyncMock

# view_all_contacts
CURRENT_USER_ID = 1
SEARCH_TERM = 'test'
CONTACT_USER_ID = 2
CONTACT_ROW = (CURRENT_USER_ID, CONTACT_USER_ID)
CONTACT = Contact(users_id=CURRENT_USER_ID, contact_user_id=CONTACT_USER_ID)

# view_contact_by_id:
CONTACT_USER_ID = 2
CONTACT_ROW = (1, CONTACT_USER_ID)
CONTACT = Contact(users_id=1, contact_user_id=CONTACT_USER_ID)

# create contact:
CURRENT_USER_ID = 1
CONTACT_USER_ID = 2

# contact_id_exists
CURRENT_USER_ID = 1
RECEIVER_ID = 2

class TestContactsService(unittest.IsolatedAsyncioTestCase):

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_view_all_contacts_no_search(self, mock_read_query):
        mock_read_query.return_value = [CONTACT_ROW]

        result = await view_all_contacts(current_user=CURRENT_USER_ID)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].users_id, CONTACT.users_id)
        self.assertEqual(result[0].contact_user_id, CONTACT.contact_user_id)

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_view_all_contacts_with_search(self, mock_read_query):
        mock_read_query.return_value = [CONTACT_ROW]

        result = await view_all_contacts(current_user=CURRENT_USER_ID, search=SEARCH_TERM)

        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], CURRENT_USER_ID)
        self.assertEqual(result[1], CONTACT_USER_ID)

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_view_all_contacts_no_results(self, mock_read_query):
        mock_read_query.return_value = []

        result = await view_all_contacts(current_user=CURRENT_USER_ID)

        self.assertIsNone(result)
    

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_view_contact_by_id_found(self, mock_read_query):
        mock_read_query.return_value = [CONTACT_ROW]

        result = await view_contact_by_id(contact_user_id=CONTACT_USER_ID)

        self.assertIsInstance(result, Contact)
        self.assertEqual(result.users_id, CONTACT.users_id)
        self.assertEqual(result.contact_user_id, CONTACT.contact_user_id)

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_view_contact_by_id_not_found(self, mock_read_query):
        mock_read_query.return_value = []

        result = await view_contact_by_id(contact_user_id=CONTACT_USER_ID)

        self.assertIsNone(result)

 
    @patch('services.contacts_service.insert_query', new_callable=AsyncMock)
    async def test_create_contact_success(self, mock_insert_query):
        mock_insert_query.return_value = CONTACT_USER_ID  # Simulate successful insertion

        result = await create_contact(contact_user_id=CONTACT_USER_ID, current_user=CURRENT_USER_ID)

        self.assertEqual(result, CONTACT_USER_ID)
        mock_insert_query.assert_called_once_with(sql=Any, sql_params=(CURRENT_USER_ID, CONTACT_USER_ID))

    @patch('services.contacts_service.insert_query', new_callable=AsyncMock)
    async def test_create_contact_failure(self, mock_insert_query):
        mock_insert_query.return_value = None  # Simulate failed insertion

        result = await create_contact(contact_user_id=CONTACT_USER_ID, current_user=CURRENT_USER_ID)

        self.assertIsNone(result)
        mock_insert_query.assert_called_once_with(sql=Any, sql_params=(CURRENT_USER_ID, CONTACT_USER_ID))


    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_contact_id_exists_true(self, mock_read_query):
        # Simulate that the contact exists
        mock_read_query.return_value = [(CURRENT_USER_ID, RECEIVER_ID)]

        result = await contact_id_exists(current_user=CURRENT_USER_ID, reciever_id=RECEIVER_ID)

        self.assertTrue(result)
        mock_read_query.assert_called_once_with(
            sql='''SELECT users_id, contact_user_id
                   FROM contacts 
                   WHERE users_id = $1 AND contact_user_id = $2''',
            sql_params=(CURRENT_USER_ID, RECEIVER_ID)
        )

    @patch('services.contacts_service.read_query', new_callable=AsyncMock)
    async def test_contact_id_exists_false(self, mock_read_query):
        # Simulate that the contact does not exist
        mock_read_query.return_value = []

        result = await contact_id_exists(current_user=CURRENT_USER_ID, reciever_id=RECEIVER_ID)

        self.assertFalse(result)
        mock_read_query.assert_called_once_with(
            sql='''SELECT users_id, contact_user_id
                   FROM contacts 
                   WHERE users_id = $1 AND contact_user_id = $2''',
            sql_params=(CURRENT_USER_ID, RECEIVER_ID)
        )
