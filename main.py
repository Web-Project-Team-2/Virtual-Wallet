from fastapi import FastAPI
from routers.categories import categories_router
from routers.users import users_router
from routers.transactions import transactions_router
import uvicorn


app = FastAPI()
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(transactions_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)




