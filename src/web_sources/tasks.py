# src/web_sources/tasks.py
from src.database import get_db
from src.utils import setup_logger
from src.web_sources.adidas.adidas import scrape_adidas
from src.web_sources.carhartt.carhartt import scrape_carhartt
from src.web_sources.converse.converse import scrape_converse
from src.web_sources.nike.nike import scrape_nike

logger = setup_logger(__name__)


async def read_sources_task():
    async for db in get_db():
        logger.info("Reading sources task started...")
        await scrape_adidas(db)
        await scrape_carhartt(db)
        await scrape_converse(db)
        await scrape_nike(db)
