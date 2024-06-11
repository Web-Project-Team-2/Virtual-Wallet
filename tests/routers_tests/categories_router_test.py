import unittest
from unittest.mock import patch, AsyncMock
from services.categories_service import get_all, create, name_exists, get_category_by_id
from data.models.categories import Category


class TestCategoriesServices(unittest.IsolatedAsyncioTestCase):

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_all_successful(self, mock_read_query):
        mock_read_query.return_value = [
            (1, "Category 1"),
            (2, "Category 2")
        ]

        categories = await get_all()

        self.assertEqual(len(categories), 2)
        self.assertIsInstance(categories[0], Category)
        self.assertEqual(categories[0].name, "Category 1")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_all_with_search(self, mock_read_query):
        mock_read_query.return_value = [
            (1, "Search Result 1")
        ]

        categories = await get_all(search="Search")

        self.assertEqual(len(categories), 1)
        self.assertIsInstance(categories[0], Category)
        self.assertEqual(categories[0].name, "Search Result 1")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_all_with_invalid_sort_by(self, mock_read_query):
        with self.assertRaises(ValueError) as context:
            await get_all(sort_by="invalid:asc")

        self.assertEqual(str(context.exception), "Invalid sort_by parameter")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_create_successful(self, mock_read_query):
        mock_read_query.return_value = [(1,)]
        category = Category(name="New Category")

        result = await create(category)

        self.assertIsInstance(result, Category)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "New Category")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_name_exists_true(self, mock_read_query):
        mock_read_query.return_value = [(1,)]

        exists = await name_exists("Existing Category")

        self.assertTrue(exists)

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_name_exists_false(self, mock_read_query):
        mock_read_query.return_value = [(0,)]

        exists = await name_exists("Nonexistent Category")

        self.assertFalse(exists)

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_category_by_id_found(self, mock_read_query):
        mock_read_query.return_value = [(1, "Found Category")]

        category = await get_category_by_id(1)

        self.assertIsInstance(category, Category)
        self.assertEqual(category.name, "Found Category")

    @patch('services.categories_service.read_query', new_callable=AsyncMock)
    async def test_get_category_by_id_not_found(self, mock_read_query):
        mock_read_query.return_value = []

        category = await get_category_by_id(1)

        self.assertIsNone(category)



