from fastapi import FastAPI

from routers.admin import admin_router
from routers.cards import cards_router
from routers.categories import categories_router
from routers.users import users_router, public_router
from routers.transactions import transactions_router
import uvicorn


app = FastAPI()
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(cards_router)
app.include_router(public_router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)




