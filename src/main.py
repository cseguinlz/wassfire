# src.main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.home.routers import router as home_router
from src.products.routers import router as product_router

# from src.scheduler import setup_scheduler
from src.scheduler import setup_scheduler
from src.web_sources.routers import router as web_sources_router
from src.whatsapp.routers import router as whatsapp_router

app_configs = {"title": "Wassfire API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["docs_url"] = None
    app_configs["redoc_url"] = None

app = FastAPI(**app_configs)


# Ping to /health to wake up the service so the publishing task runs.
@app.get("/health")
def health_check():
    """
    Health check endpoint to ensure the service is up and running.
    """
    return JSONResponse(content={"status": "UP"}, status_code=200)


# Setup scheduled tasks
setup_scheduler(app)

# routers
app.include_router(product_router, prefix="/api/v1", tags=["crud"])
app.include_router(web_sources_router, prefix="/web-sources", tags=["web-sources"])
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(home_router, tags=["home"])


app.mount("/static", StaticFiles(directory="static"), name="static")
