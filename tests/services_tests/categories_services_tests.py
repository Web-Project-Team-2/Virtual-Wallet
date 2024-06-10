import unittest
from unittest.mock import patch, AsyncMock
from services.categories_service import get_all, create, name_exists, Category

class TestCategoriesService(unittest.IsolatedAsyncioTestCase):
    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_all_categories(self, mock_read_query):
        # Mock data
        mock_category_data = [(1, "Category 1"), (2, "Category 2")]
        mock_read_query.return_value = mock_category_data

        # Call the function
        result = await get_all()

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Category)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].name, "Category 1")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_create_category(self, mock_read_query):
        # Mock data
        mock_category = Category(id=1, name="Category 1")
        mock_read_query.return_value = [(1,)]

        # Call the function
        result = await create(mock_category)

        # Assertions
        self.assertIsInstance(result, Category)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Category 1")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_name_exists(self, mock_read_query):
        # Mock data
        mock_read_query.return_value = [(1,)]

        # Call the function
        result = await name_exists("Category 1")

        # Assertions
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
