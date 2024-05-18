from fastapi import APIRouter, Depends, Response, status, HTTPException

from schemas.cards import CardCreate
from services.cards_services import create
from common import authorization
from data.models.cards import Card

cards_router = APIRouter(prefix="/cards")


@cards_router.post('/')
def create_card(card_details: CardCreate, current_user: int = Depends(authorization.get_current_user)):
    try:
        create(**card_details.to_dict(), user_id=current_user)
        return Response(f"Successfully created", status_code=status.HTTP_201_CREATED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to create card")
