# src.main.py
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.home.routers import router as home_router
from src.products.routers import router as product_router
from src.web_sources.routers import router as web_sources_router
from src.whatsapp.routers import router as whatsapp_router

app = FastAPI()


# Middleware to detect user's locale
def get_user_locale(request: Request) -> str:
    return request.headers.get("Accept-Language", "en").split(",")[0]


@app.middleware("http")
async def add_process_locale(request: Request, call_next: Callable):
    response = await call_next(request)
    locale = get_user_locale(request)
    # print(f"locale: {locale}")
    request.state.locale = locale
    return response


# Setup scheduled tasks
# setup_scheduler(app)

# routers
app.include_router(product_router, prefix="/api/v1", tags=["crud"])
app.include_router(web_sources_router, prefix="/web-sources", tags=["web-sources"])
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(home_router, tags=["home"])


app.mount("/static", StaticFiles(directory="static"), name="static")
