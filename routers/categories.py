from fastapi import APIRouter, Depends
from data.models.categories import Category
from common import responses, authorization
from services import categories_service
from http import HTTPStatus

categories_router = APIRouter(prefix="/categories")


@categories_router.get('/')
def get_categories(search: str = None, sort_by: str = None, page: int = 1, size: int = 10):
    return categories_service.get_all(search, sort_by, page, size)


@categories_router.post('/', status_code=201)
def create_category(category: Category, current_user: int = Depends(authorization.get_current_user)):
    if current_user is None:
        raise HTTPStatus.FORBIDDEN
    if categories_service.name_exists(category.name):
        return responses.BadRequest("Category with that name already exists")

    _category = categories_service.create(category)
    if _category is None:
        return responses.BadRequest("")

    return _category


@categories_router.get('/{id}')
def get_category_by_id(id: int):
    return categories_service.find_category_by_id(id)
