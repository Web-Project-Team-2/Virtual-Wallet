from fastapi import APIRouter, status, HTTPException, Depends
import security.password_hashing
import services.user_services
from common import authorization
from common.authorization import create_access_token
from common.helper_functions import check_password
from common.wallet_info import detailed_info
from schemas.contact import ContactCreate
from schemas.deposit import Deposit
from schemas.transactions import TransactionFilters
from schemas.withdraw import WithdrawMoney
from services.user_services import view
from schemas.user import UserCreate, UserOut, UserLogin, UserInfoUpdate
from security.password_hashing import verify_password
from services import user_services
from services.user_services import view_profile, update_profile, deposit_money, withdraw_money, view_user_transactions

users_router = APIRouter(prefix='/users')
public_router = APIRouter()


@users_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut, tags=["Users"])
def register(user_create: UserCreate):
    check_password(user_create.password)

    hashed_password = security.password_hashing.get_password_hash(user_create.password)
    user_create.password = hashed_password

    new_user = user_services.create(user_create.username, user_create.password, user_create.email,
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
def login(user_credentials: UserLogin):
    user = services.user_services.try_login(user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/credit', tags=["Users"])
def view_credit_info(current_user: int = Depends(authorization.get_current_user)):
    try:
        view_info_result = view(current_user)
        return view_info_result
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to show credit information")


@users_router.get('/info', tags=["Users"])
def view_user_info(current_user: int = Depends(authorization.get_current_user)):
    try:
        view_info_result = view_profile(current_user)
        return view_info_result
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to show user information")


@public_router.get('/info', tags=["Public"])
def get_detailed_info():
    return detailed_info


@users_router.post('/create', status_code=status.HTTP_201_CREATED, tags=["Contacts"])
def create_contact(contact_create: ContactCreate, current_user: int = Depends(authorization.get_current_user)):
    contact_created = user_services.create_contact(current_user, contact_create.contact_user_id)

    if not contact_created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to create contact. The user might already be a contact or does not exist.")

    return {"message": "Contact created successfully", "contact_username": contact_created["contact_username"]}


@users_router.delete('/contacts/{contact_user_id}', status_code=status.HTTP_200_OK, tags=["Contacts"])
def delete_contact(contact_user_id: int, current_user: int = Depends(authorization.get_current_user)):
    contact_deleted = user_services.delete_contact(current_user, contact_user_id)

    if not contact_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to delete contact. The contact does not exist.")

    return {"message": "Contact deleted successfully"}


@users_router.get('/contacts', status_code=status.HTTP_200_OK, tags=["Contacts"])
def get_all_contacts(current_user: int = Depends(authorization.get_current_user)):
    contacts = user_services.get_all_contacts(current_user)

    if contacts is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to fetch contacts.")

    return {"contacts": contacts}


@users_router.put('/update', tags=["Users"])
def update_user_info(user: UserInfoUpdate, current_user: int = Depends(authorization.get_current_user)):
    check_password(user.password)

    hashed_password = security.password_hashing.get_password_hash(user.password)
    user.password = hashed_password

    try:
        update = update_profile(current_user, user.email, user.password, user.phone_number)
        return update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update user information")


@users_router.put('/deposit', tags=["Users"])
def deposit(money: Deposit, current_user: int = Depends(authorization.get_current_user)):
    try:
        deposit_update = deposit_money(current_user, money.deposit_money)
        return deposit_update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to deposit money.")


@users_router.put('/withdraw', tags=["Users"])
def withdraw(money: WithdrawMoney, current_user: int = Depends(authorization.get_current_user)):
    try:
        withdraw_update = withdraw_money(current_user, money.withdraw_money)
        return withdraw_update
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to withdraw money.")


@users_router.get('/admin/{user_id}', tags=["Users"])
def get_user_transactions_(
    user_id: int,
    current_user: int = Depends(authorization.get_current_user),
    filters: TransactionFilters = Depends()
):
    result = view_user_transactions(user_id, current_user, filters)

    if isinstance(result, str):
        raise HTTPException(status_code=403, detail=result)

    return result
