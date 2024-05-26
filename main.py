from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from common.wallet_info import detailed_info
from routers.admin import admin_router
from routers.cards import cards_router
from routers.categories import categories_router
from routers.users import users_router, public_router
from routers.transactions import transactions_router
from routers.recurring_transactions import recurring_transactions_router
import uvicorn



app = FastAPI()
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(recurring_transactions_router)
app.include_router(cards_router)
app.include_router(public_router)
app.include_router(admin_router)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home_page.html", {"request": request, "detailed_info": detailed_info})


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8001)




