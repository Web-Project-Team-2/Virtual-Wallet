from fastapi import APIRouter, Depends
from data.models.categories import Category
from common import responses, authorization
from services import categories_service

categories_router = APIRouter(prefix="/categories")


@categories_router.get('/')
def get_categories(search: str = None, sort_by: str = None, page: int = 1, size: int = 10):
    return categories_service.get_all(search, sort_by, page, size)


@categories_router.post('/', status_code=201)
def create_category(category: Category):
    if categories_service.name_exists(category.name):
        return responses.BadRequest("Category with that name already exists")

    return categories_service.create(category)


