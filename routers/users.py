from fastapi import APIRouter, status, HTTPException, Depends

import security.password_hashing
import services.user_services
from common import authorization
from common.authorization import create_access_token
from services.user_services import view
from data.models.cards import Card
from schemas.user import UserCreate, UserOut, UserLogin
from security.password_hashing import verify_password
from services import user_services

users_router = APIRouter(prefix='/users')


@users_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserOut, tags=["Users"])
def register(user_create: UserCreate):
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


@users_router.get('/info', tags=["Users"])
def view_info(current_user: int = Depends(authorization.get_current_user)):
    try:
        view_info_result = view(current_user)
        return view_info_result
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to show credit information")


