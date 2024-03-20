from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.web_sources.adidas.adidas import scrape_adidas

router = APIRouter()


@router.post("/read-adidas/")
async def read_adidas(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(scrape_adidas, db)
    return {"message": "Scraping started with start index {}"}
