from fastapi import APIRouter, status, HTTPException, Depends
import security.password_hashing
import services.user_services
from common import authorization
from common.authorization import create_access_token
from common.helper_functions import check_password
from common.wallet_info import detailed_info
from schemas.contact import ContactCreate
from services.user_services import view
from schemas.user import UserCreate, UserOut, UserLogin
from security.password_hashing import verify_password
from services import user_services
from services.user_services import view_profile
from services import admin_services

admin_router = APIRouter(prefix='/admin')


@admin_router.get("/all_users")
def get_all_users(search: str = None, page: int = 1, size: int = 10,
                  current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    admin_services.get_all_users(search, page, size)


@admin_router.put("/block/{user_id}")
def block_user(user_id: int, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.block_user(user_id)


@admin_router.put("/unblock/{user_id}")
def unblock_user(user_id: int, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.unblock_user(user_id)


@admin_router.put("/approve/{email}")
def approve_user(email: str, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.approve_user(email)
