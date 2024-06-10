from fastapi import APIRouter, Depends, Response, status, HTTPException
from schemas.cards import CardCreate
from services.cards_services import create, delete
from common import authorization

cards_router = APIRouter(prefix="/api/cards")

@cards_router.post('/', tags=["Cards"])
async def create_card(card_details: CardCreate, current_user: int = Depends(authorization.get_current_user)):
    try:
        await create(**card_details.dict(), user_id=current_user)
        return Response(f"Successfully created", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to create card: {e}")

@cards_router.delete('/{card_id}', tags=["Cards"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int, current_user: int = Depends(authorization.get_current_user)):
    try:
        success = await delete(card_id, current_user)
        if success:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to delete card: {e}")

