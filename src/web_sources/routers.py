from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.web_sources.adidas.adidas import scrape_adidas
from src.web_sources.carhartt.carhartt import scrape_carhartt
from src.web_sources.converse.converse import scrape_converse
from src.web_sources.nike.nike import scrape_nike

router = APIRouter()


@router.post("/read-adidas/")
async def read_adidas(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(scrape_adidas, db)
    return {"message": "Scraping started with start index {}"}


@router.post("/read-carhartt/")
async def read_carhartt(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(scrape_carhartt, db)
    return {"message": "Scraping started with start index {}"}


@router.post("/read-converse/")
async def read_converse(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(scrape_converse, db)
    return {"message": "Scraping started with start index {}"}


@router.post("/read-nike/")
async def read_nike(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(scrape_nike, db)
    return {"message": "Scraping started with start index {}"}
