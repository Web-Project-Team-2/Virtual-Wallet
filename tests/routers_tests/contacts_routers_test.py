import unittest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status
from typing import List
from schemas.contacts import ContactView
from routers.contacts import get_users_contacts, get_users_contact_by_id, create_contact
from data.models.contacts import Contact
from common.responses import NotFound


class TestContactsRouter(unittest.IsolatedAsyncioTestCase):

    @patch('services.contacts_service.view_all_contacts', new_callable=AsyncMock)
    @patch('services.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_contacts_successful(self, mock_get_user_by_id, mock_view_all_contacts):
        # Mock data
        mock_view_all_contacts.return_value = [
            Contact(contact_user_id=1),
            Contact(contact_user_id=2)
        ]
        mock_get_user_by_id.side_effect = [
            AsyncMock(username='user1'),
            AsyncMock(username='user2')
        ]

        # Call the function
        result = await get_users_contacts(search=None, current_user=1)

        # Assert the results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].username, 'user1')
        self.assertEqual(result[1].username, 'user2')

    @patch('services.contacts_service.view_all_contacts', new_callable=AsyncMock)
    @patch('services.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_contacts_search(self, mock_get_user_by_id, mock_view_all_contacts):
        # Mock data
        mock_view_all_contacts.return_value = [
            Contact(contact_user_id=1)
        ]
        mock_get_user_by_id.return_value = AsyncMock(username='searched_user')

        # Call the function
        result = await get_users_contacts(search='searched', current_user=1)

        # Assert the results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].username, 'searched_user')

    @patch('services.contacts_service.view_all_contacts', new_callable=AsyncMock)
    async def test_get_users_contacts_no_contacts(self, mock_view_all_contacts):
        # Mock data
        mock_view_all_contacts.return_value = []

        # Call the function
        with self.assertRaises(HTTPException) as context:
            await get_users_contacts(search=None, current_user=1)

        # Assert the results
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, 'There are no available contacts.')

    @patch('services.contacts_service.view_all_contacts', new_callable=AsyncMock)
    @patch('services.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_contacts_contact_not_available(self, mock_get_user_by_id, mock_view_all_contacts):
        # Mock data
        mock_view_all_contacts.return_value = [
            Contact(contact_user_id=1)
        ]
        mock_get_user_by_id.return_value = None

        # Call the function
        with self.assertRaises(HTTPException) as context:
            await get_users_contacts(search=None, current_user=1)

        # Assert the results
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, 'This contact is not available.')

    
    @patch('routers.contacts.contacts_service.contact_id_exists', new_callable=AsyncMock)
    @patch('routers.contacts.contacts_service.view_contact_by_id', new_callable=AsyncMock)
    @patch('routers.contacts.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_get_users_contact_by_id_successful(self, mock_get_user_by_id, mock_view_contact_by_id, mock_contact_id_exists):
        # Mocking the return values
        mock_contact_id_exists.return_value = True
        mock_view_contact_by_id.return_value = {
            "username": "test_user",
            "email": "test_user@example.com",
            "phone_number": "123456789"
        }
        mock_get_user_by_id.return_value = {
            "username": "test_user",
            "email": "test_user@example.com",
            "phone_number": "123456789"
        }
        
        # Call the function
        result = await get_users_contact_by_id(contact_user_id=1, current_user=2)
        
        # Assertions
        self.assertEqual(result, [ContactView.contacts_view(username="test_user", email="test_user@example.com", phone_number="123456789")])

    @patch('routers.contacts.contacts_service.contact_id_exists', new_callable=AsyncMock)
    async def test_get_users_contact_by_id_not_found(self, mock_contact_id_exists):
        # Mocking the return value
        mock_contact_id_exists.return_value = False
        
        # Call the function and expect an exception
        result = await get_users_contact_by_id(contact_user_id=1, current_user=2)
        
        # Assertions
        self.assertEqual(result, NotFound(content='The contact you are looking for is not available.'))

    @patch('routers.contacts.contacts_service.contact_id_exists', new_callable=AsyncMock)
    @patch('routers.contacts.contacts_service.view_contact_by_id', new_callable=AsyncMock)
    async def test_get_users_contact_by_id_no_data(self, mock_view_contact_by_id, mock_contact_id_exists):
        # Mocking the return values
        mock_contact_id_exists.return_value = True
        mock_view_contact_by_id.return_value = None
        
        # Call the function
        result = await get_users_contact_by_id(contact_user_id=1, current_user=2)
        
        # Assertions
        self.assertEqual(result, NotFound(content='Required data not found.'))


    @patch('routers.contacts.user_services.user_id_exists', new_callable=AsyncMock)
    @patch('routers.contacts.contacts_service.create_contact', new_callable=AsyncMock)
    @patch('routers.contacts.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_create_contact_successful(self, mock_get_user_by_id, mock_create_contact, mock_user_id_exists):
        # Mocking the return values
        mock_user_id_exists.return_value = True
        mock_create_contact.return_value = AsyncMock()
        mock_get_user_by_id.return_value = {
            "username": "test_user",
            "email": "test_user@example.com",
            "phone_number": "123456789"
        }
        
        contact = Contact(contact_user_id=1)
        result = await create_contact(contact=contact, current_user=2)
        
        # Assertions
        self.assertEqual(result, [ContactView.contacts_view(username="test_user", email="test_user@example.com", phone_number="123456789")])

    @patch('routers.contacts.user_services.user_id_exists', new_callable=AsyncMock)
    async def test_create_contact_user_not_found(self, mock_user_id_exists):
        # Mocking the return value
        mock_user_id_exists.return_value = False
        
        contact = Contact(contact_user_id=1)
        result = await create_contact(contact=contact, current_user=2)
        
        # Assertions
        self.assertEqual(result, NotFound(content='The contact you are looking for is not available.'))

    @patch('routers.contacts.user_services.user_id_exists', new_callable=AsyncMock)
    @patch('routers.contacts.contacts_service.create_contact', new_callable=AsyncMock)
    @patch('routers.contacts.user_services.get_user_by_id', new_callable=AsyncMock)
    async def test_create_contact_no_data(self, mock_get_user_by_id, mock_create_contact, mock_user_id_exists):
        # Mocking the return values
        mock_user_id_exists.return_value = True
        mock_create_contact.return_value = AsyncMock()
        mock_get_user_by_id.return_value = None
        
        contact = Contact(contact_user_id=1)
        result = await create_contact(contact=contact, current_user=2)
        
        # Assertions
        self.assertEqual(result, NotFound(content='Required data not found.'))