from fastapi import APIRouter, Depends, HTTPException, Response, status
from data.models.categories import Category
from common import responses, authorization
from services import categories_service
from http import HTTPStatus

categories_router = APIRouter(prefix="/api/categories")


@categories_router.get('/', tags=["Categories"])
async def get_categories(search: str = None, sort_by: str = None, page: int = 1, size: int = 10):
    '''
         This function returns all the available categories.
    '''
    return await categories_service.get_all(search, sort_by, page, size)


@categories_router.post('/', status_code=201, tags=["Categories"])
async def create_category(category: Category, current_user: int = Depends(authorization.get_current_user)):
    '''
             This function creates new category. To create category you should be registered and logged.
    '''
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if await categories_service.name_exists(category.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with that name already exists")

    _category = await categories_service.create(category)
    if _category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to create category")

    return _category
