from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError

from common.authorization import create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from security import password_hashing
from security.password_hashing import get_password_hash, verify_password
from schemas.user import UserCreate
from services import user_services
from common.helper_functions import check_password

templates = Jinja2Templates(directory="templates")
frontend_router = APIRouter()

@frontend_router.get("/register", response_class=HTMLResponse)
async def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@frontend_router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), phone_number: str = Form(...)):
    user_create = UserCreate(username=username, password=password, email=email, phone_number=phone_number)
    check_password(user_create.password)

    hashed_password = password_hashing.get_password_hash(user_create.password)
    user_create.password = hashed_password

    new_user = await user_services.create(user_create.username, user_create.password, user_create.email, user_create.phone_number)

    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username, email, or phone number is already taken.")

    return RedirectResponse(url=f"/?message=User registered successfully!", status_code=status.HTTP_303_SEE_OTHER)

@frontend_router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@frontend_router.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await user_services.try_login(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid credentials"})

    access_token = create_access_token(data={"user_id": user.id})
    response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)  # Use httponly for security
    return response

@frontend_router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: int = Depends(get_current_user)):
    user_info = await user_services.view_profile(current_user)
    card_info = await user_services.view(current_user)  # Fetch card and transaction info

    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return templates.TemplateResponse("profile.html", {"request": request, "user": user_info, "card_info": card_info})