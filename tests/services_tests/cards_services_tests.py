import unittest
from unittest.mock import patch, AsyncMock
from services.cards_services import create, delete, get_card_by_id
from data.models.cards import Card


class TestCardServices(unittest.IsolatedAsyncioTestCase):

    @patch('services.cards_services.insert_query', new_callable=AsyncMock)
    @patch('services.user_services.read_query', new_callable=AsyncMock)
    async def test_create_card_success(self, mock_read_query, mock_insert_query):
        mock_id = 1
        mock_insert_query.return_value = mock_id
        mock_read_query.return_value = [(1, "1234567812345678", "DANI DIMITROV", "123", "2028-07-01", "active", 1, 0)]

        result = await create("1234567812345678", "DANI DIMITROV", "123", "07/28"
                              , 1)

        self.assertEqual(result.id, mock_id)
        self.assertEqual(str(result.card_number), "1234567812345678")
        self.assertEqual(str(result.cvv), "123")
        self.assertEqual(str(result.card_holder), "DANI DIMITROV")
        self.assertEqual(str(result.expiration_date), "2028-07-01")
        self.assertEqual(str(result.card_status), "active")
        self.assertEqual(result.user_id, 1)
        self.assertEqual(result.balance, 100.0)


    @patch('services.cards_services.delete_query', new_callable=AsyncMock)
    async def test_delete_card_success(self, mock_delete_query):
        mock_delete_query.return_value = True

        result = await delete(1, 1)
        self.assertTrue(result)
        mock_delete_query.assert_called_once_with('DELETE FROM cards WHERE id = $1 AND user_id = $2', (1, 1))

    @patch('services.cards_services.delete_query', new_callable=AsyncMock)
    async def test_delete_card_failure(self, mock_delete_query):
        mock_delete_query.side_effect = Exception("Deletion failed")

        with self.assertRaises(Exception) as context:
            await delete(1, 1)

        self.assertEqual(str(context.exception), "Error deleting card: Deletion failed")
        mock_delete_query.assert_called_once_with('DELETE FROM cards WHERE id = $1 AND user_id = $2', (1, 1))

    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_by_id_success(self, mock_read_query):
        mock_card_data = [(1, "1234567812345678", "123", "DANI DIMITROV", "2028-07-01", "active", 1, 100.0)]
        mock_read_query.return_value = mock_card_data

        result = await get_card_by_id(1)
        self.assertIsInstance(result, Card)
        self.assertEqual(result.id, 1)
        self.assertEqual(str(result.card_number), "1234567812345678")
        self.assertEqual(str(result.cvv), "123")
        self.assertEqual(str(result.card_holder), "DANI DIMITROV")
        self.assertEqual(str(result.expiration_date), "2028-07-01")
        self.assertEqual(str(result.card_status), "active")
        self.assertEqual(result.user_id, 1)
        self.assertEqual(result.balance, 100.0)

    @patch('services.cards_services.read_query', new_callable=AsyncMock)
    async def test_get_card_by_id_failure(self, mock_read_query):
        mock_read_query.return_value = []

        result = await get_card_by_id(1)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
