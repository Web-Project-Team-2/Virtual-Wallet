from fastapi import APIRouter, status, HTTPException, Depends, Form, Request
from starlette.responses import HTMLResponse, RedirectResponse

import security.password_hashing
from common import authorization
from common.authorization import create_access_token, get_current_user
from common.helper_functions import check_password
from common.wallet_info import detailed_info
from routers.frontend import templates
from schemas.contacts import ContactCreate
from schemas.deposit import Deposit
from schemas.withdraw import WithdrawMoney
from schemas.user import UserCreate, UserLogin, UserInfoUpdate, UserOut

from services import user_services

users_router = APIRouter(prefix='/api/users')
public_router = APIRouter()



@users_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut, tags=["Users"])
async def register(user_create: UserCreate):
    check_password(user_create.password)

    hashed_password = security.password_hashing.get_password_hash(user_create.password)
    user_create.password = hashed_password

    new_user = await user_services.create(user_create.username, user_create.password, user_create.email,
                                          user_create.phone_number)

    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username, email, or phone number is already taken.")

    return UserOut(
        email=new_user.email,
        username=new_user.username,
        phone_number=new_user.phone_number
    )


@users_router.post('/login', tags=["Users"])
async def login(user_credentials: UserLogin):
    user = await user_services.try_login(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/credit', tags=["Users"])
async def view_credit_info(current_user: int = Depends(authorization.get_current_user)):
    try:
        view_info_result = await user_services.view(current_user)
        return view_info_result
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to show credit information")


@users_router.get('/info', tags=["Users"])
async def view_user_info(current_user: int = Depends(get_current_user)):
    try:
        view_info_result = await user_services.view_profile(current_user)
        return view_info_result
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to show user information")


@public_router.get('/info', tags=["Public"])
def get_detailed_info():
    return detailed_info


@users_router.post('/create', status_code=status.HTTP_201_CREATED, tags=["Contacts"])
async def create_contact(contact_create: ContactCreate, current_user: int = Depends(authorization.get_current_user)):
    contact_created = await user_services.create_contact(current_user, contact_create.contact_user_id)

    if not contact_created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create contact. The user might already be a contact or does not exist."
        )

    return {"message": "Contact created successfully", "contact_username": contact_created["contact_username"]}


@users_router.delete('/contacts/{contact_user_id}', status_code=status.HTTP_200_OK, tags=["Contacts"])
async def delete_contact(contact_user_id: int, current_user: int = Depends(authorization.get_current_user)):
    contact_deleted = await user_services.delete_contact(current_user, contact_user_id)

    if not contact_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to delete contact. The contact does not exist.")

    return {"message": "Contact deleted successfully"}


@users_router.get('/contacts', status_code=status.HTTP_200_OK, tags=["Contacts"])
async def get_all_contacts(current_user: int = Depends(authorization.get_current_user)):
    contacts = await user_services.get_all_contacts(current_user)

    if contacts is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to fetch contacts.")

    return {"contacts": contacts}


@users_router.put('/update', tags=["Users"])
async def update_user_info(user: UserInfoUpdate, current_user: int = Depends(authorization.get_current_user)):
    check_password(user.password)

    hashed_password = security.password_hashing.get_password_hash(user.password)
    user.password = hashed_password

    try:
        update = await user_services.update_profile(current_user, user.email, user.password, user.phone_number)
        return update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update user information")


@users_router.put('/deposit', tags=["Users"])
async def deposit(money: Deposit, current_user: int = Depends(authorization.get_current_user)):
    try:
        deposit_update = await user_services.deposit_money(current_user, money.deposit_money)
        return deposit_update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to deposit money.")


@users_router.put('/withdraw', tags=["Users"])
async def withdraw(money: WithdrawMoney, current_user: int = Depends(authorization.get_current_user)):
    try:
        withdraw_update = await user_services.withdraw_money(current_user, money.withdraw_money)
        return withdraw_update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to withdraw money.")
