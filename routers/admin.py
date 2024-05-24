from fastapi import APIRouter, status, HTTPException, Depends
from common import authorization
from schemas.transactions import TransactionFilters
from services import admin_services
from services.admin_services import view_user_transactions, pending_transactions

admin_router = APIRouter(prefix='/admin')


@admin_router.get("/all_users", tags=["Admin"])
def get_all_users(search: str = None, page: int = 1, size: int = 10,
                  current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    admin_services.get_all_users(search, page, size)


@admin_router.put("/block/{user_id}", tags=["Admin"])
def block_user(user_id: int, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.block_user(user_id)


@admin_router.put("/unblock/{user_id}", tags=["Admin"])
def unblock_user(user_id: int, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.unblock_user(user_id)


@admin_router.put("/approve/{email}", tags=["Admin"])
def approve_user(email: str, current_user: int = Depends(authorization.get_current_user)):
    if admin_services.check_if_not_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have admin permissions"
        )

    return admin_services.approve_user(email)


@admin_router.get('/transactions/{user_id}', tags=["Admin"])
def get_user_transactions_(
        user_id: int,
        current_user: int = Depends(authorization.get_current_user),
        filters: TransactionFilters = Depends()
):
    result = view_user_transactions(user_id, current_user, filters)

    if isinstance(result, str):
        raise HTTPException(status_code=403, detail=result)

    return result


@admin_router.post('/deny/{user_id}', tags=["Admin"])
def deny_user_pending_transactions(
        user_id: int,
        current_user: int = Depends(authorization.get_current_user)
):
    result = pending_transactions(current_user, user_id)

    if isinstance(result, str) and result.startswith("Not authorized"):
        raise HTTPException(status_code=403, detail=result)
    elif isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {"message": result}
