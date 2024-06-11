import unittest
from unittest.mock import patch, AsyncMock
from services.cards_services import create, delete, get_card_by_id, get_card_info_by_id, get_card_by_user_id
from data.models.cards import Card


class TestCardsServices(unittest.IsolatedAsyncioTestCase):


    @patch('services.cards_services.delete_query', new_callable=AsyncMock)
    async def test_delete_successful(self, mock_delete_query):
        mock_delete_query.return_value = True

        result = await delete(card_id=1, user_id=1)

        self.assertTrue(result)
        mock_delete_query.assert_called_once_with('DELETE FROM cards WHERE id = $1 AND user_id = $2', (1, 1))

    @patch('services.cards_services.delete_query', new_callable=AsyncMock)
    async def test_delete_failure(self, mock_delete_query):
        mock_delete_query.side_effect = Exception("Deletion error")

        with self.assertRaises(Exception) as context:
            await delete(card_id=1, user_id=1)

        self.assertEqual(str(context.exception), "Error deleting card: Deletion error")

    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_by_id_found(self, mock_read_query):
        mock_read_query.return_value = [(1, "1234567890123456", "123", "John Doe", "2024-12-31", "active", 1, 100)]

        card = await get_card_by_id(card_id=1)

        self.assertIsInstance(card, Card)
        self.assertEqual(card.card_number, 1234567890123456)

    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_by_id_not_found(self, mock_read_query):
        mock_read_query.return_value = []

        card = await get_card_by_id(card_id=1)

        self.assertIsNone(card)


    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_info_by_id_not_found(self, mock_read_query):
        mock_read_query.return_value = []

        card = await get_card_info_by_id(card_id=1)

        self.assertIsNone(card)

    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_by_user_id_found(self, mock_read_query):
        mock_read_query.return_value = [(1, "1234567890123456", "123", "John Doe", "2024-12-31", "active", 1, 100)]

        card_id = await get_card_by_user_id(cards_user_id=1)

        self.assertEqual(card_id, 1)

