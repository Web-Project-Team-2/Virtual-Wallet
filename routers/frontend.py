from fastapi import APIRouter, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from common.authorization import create_access_token, get_current_user
from schemas.cards import CardCreate
from security import password_hashing
from schemas.user import UserCreate
from services import user_services
from common.helper_functions import check_password, get_card_id_by_card_number
from services.cards_services import create, delete

templates = Jinja2Templates(directory="templates")
frontend_router = APIRouter()


@frontend_router.get("/register", response_class=HTMLResponse, tags=['Frontend'])
async def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@frontend_router.post("/register", response_class=HTMLResponse, tags=['Frontend'])
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...),
                        phone_number: str = Form(...)):
    try:
        user_create = UserCreate(username=username, password=password, email=email, phone_number=phone_number)
        check_password(user_create.password)
        hashed_password = password_hashing.get_password_hash(user_create.password)
        user_create.password = hashed_password
        new_user = await user_services.create(user_create.username, user_create.password, user_create.email,
                                              user_create.phone_number)
        if not new_user:
            return templates.TemplateResponse("register.html", {"request": request, "error_message": "Username, email, or phone number is already taken."})

        # Generate token for the newly registered user
        access_token = create_access_token(data={"user_id": new_user.id})

        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=access_token, httponly=True)  # Use httponly for security

        return response
    except HTTPException as e:
        return templates.TemplateResponse("register.html", {"request": request, "error_message": e.detail})
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error_message": "An unexpected error occurred. Please try again."})




@frontend_router.get("/login", response_class=HTMLResponse, tags=['Frontend'])
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@frontend_router.post("/login", response_class=HTMLResponse, tags=['Frontend'])
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await user_services.try_login(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid credentials"})
    access_token = create_access_token(data={"user_id": user.id})
    response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)  # Use httponly for security
    return response


@frontend_router.get("/profile", response_class=HTMLResponse, tags=['Frontend'])
async def profile(request: Request, current_user: int = Depends(get_current_user)):
    user_info = await user_services.view_profile(current_user)
    card_info = await user_services.view(current_user)  # Fetch card and transaction info
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user_info, "card_info": card_info})


@frontend_router.get("/edit-profile", response_class=HTMLResponse, tags=['Frontend'])
async def edit_profile_form(request: Request, current_user: int = Depends(get_current_user)):
    user_info = await user_services.view_profile(current_user)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": user_info})


@frontend_router.post("/edit-profile", response_class=HTMLResponse, tags=['Frontend'])
async def edit_profile(request: Request, email: str = Form(...), password: str = Form(...),
                       phone_number: str = Form(...), current_user: int = Depends(get_current_user)):
    check_password(password)
    hashed_password = password_hashing.get_password_hash(password)
    update_result = await user_services.update_profile(current_user, email, hashed_password, phone_number)
    if update_result != "User information updated successfully":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update user information")
    return RedirectResponse(url="/profile?message=success", status_code=status.HTTP_303_SEE_OTHER)


@frontend_router.get("/deposit", response_class=HTMLResponse, tags=['Frontend'])
async def get_deposit_form(request: Request, current_user: int = Depends(get_current_user)):
    return templates.TemplateResponse("deposit.html", {"request": request})


@frontend_router.post("/deposit", response_class=HTMLResponse, tags=['Frontend'])
async def deposit_funds(request: Request, amount: float = Form(...), current_user: int = Depends(get_current_user)):
    if amount < 25:
        return templates.TemplateResponse("deposit.html",
                                          {"request": request, "error_message": "Minimum deposit is $25."})

    deposit_result = await user_services.deposit_money(current_user, int(amount))
    if "successfully" not in deposit_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=deposit_result)

    return RedirectResponse(url="/profile?message=success", status_code=status.HTTP_303_SEE_OTHER)


@frontend_router.get("/withdraw", response_class=HTMLResponse, tags=['Frontend'])
async def get_withdraw_form(request: Request, current_user: int = Depends(get_current_user)):
    return templates.TemplateResponse("withdraw.html", {"request": request})


@frontend_router.post("/withdraw", response_class=HTMLResponse, tags=['Frontend'])
async def withdraw_funds(request: Request, amount: float = Form(...), current_user: int = Depends(get_current_user)):
    withdraw_result = await user_services.withdraw_money(current_user, int(amount))
    if "successfully" not in withdraw_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=withdraw_result)
    return JSONResponse(content={"message": "success"}, status_code=status.HTTP_200_OK)


@frontend_router.get("/logout", response_class=HTMLResponse, tags=['Frontend'])
async def logout(request: Request):
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    return response


@frontend_router.post("/cards", response_class=HTMLResponse, tags=['Frontend'])
async def create_card(request: Request, current_user: int = Depends(get_current_user)):
    form = await request.json()
    card_number = form.get("card_number")
    card_holder = form.get("card_holder")
    cvv = form.get("cvv")
    expiration_date = form.get("expiration_date")

    card_create = CardCreate(card_number=card_number, card_holder=card_holder, cvv=cvv, expiration_date=expiration_date)

    try:
        await create(**card_create.dict(), user_id=current_user)
        return RedirectResponse(url="/profile?message=card_created", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to create card: {e}")






