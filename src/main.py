# src.main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.home.routers import router as home_router
from src.products.routers import router as product_router
from src.web_sources.routers import router as web_sources_router
from src.whatsapp.routers import router as whatsapp_router

app_configs = {"title": "Wassfire API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["docs_url"] = None
    app_configs["redoc_url"] = None

app = FastAPI(**app_configs)

# Setup scheduled tasks
# setup_scheduler(app)

# routers
app.include_router(product_router, prefix="/api/v1", tags=["crud"])
app.include_router(web_sources_router, prefix="/web-sources", tags=["web-sources"])
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(home_router, tags=["home"])


app.mount("/static", StaticFiles(directory="static"), name="static")
