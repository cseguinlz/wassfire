# src.home.routers.py

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import Subscriber
from src.utils import get_translations

router = APIRouter()
templates = Jinja2Templates(directory="src/templates/home")


@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request, translations: dict = Depends(get_translations)):
    return templates.TemplateResponse("home.html", {"request": request, **translations})


@router.get("/tos", response_class=HTMLResponse)
async def get_tos(request: Request, translations: dict = Depends(get_translations)):
    return templates.TemplateResponse("tos.html", {"request": request, **translations})


@router.get("/privacy", response_class=HTMLResponse)
async def get_privacy(request: Request, translations: dict = Depends(get_translations)):
    return templates.TemplateResponse(
        "privacy.html", {"request": request, **translations}
    )


@router.get("/brands", response_class=HTMLResponse)
async def get_brands(request: Request, translations: dict = Depends(get_translations)):
    return templates.TemplateResponse(
        "brands.html", {"request": request, **translations}
    )


@router.post("/submit-email")
async def submit_email(email: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        new_subscriber = Subscriber(email=email)
        db.add(new_subscriber)
        await db.commit()
        # Success message
        content = "<p>Thank you for subscribing!</p>"
    except IntegrityError:
        await db.rollback()
        # Error message for duplicate email
        content = "<p>Email is already subscribed.</p>"
    except Exception as e:
        await db.rollback()
        # General error message
        content = f"<p>An error occurred: {str(e)}</p>"

    return HTMLResponse(content=content, status_code=200)
