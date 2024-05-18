from fastapi import FastAPI

from routers.cards import cards_router
from routers.categories import categories_router
from routers.users import users_router
import uvicorn


app = FastAPI()
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(cards_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)




