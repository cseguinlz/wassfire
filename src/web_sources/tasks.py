from src.utils import setup_logger
from src.web_sources.adidas.adidas import scrape_adidas
from src.web_sources.carhartt.carhartt import scrape_carhartt
from src.web_sources.converse.converse import scrape_converse
from src.web_sources.nike.nike import scrape_nike

# Initialize logger
logger = setup_logger(__name__)


async def read_sources_task():
    logger.info("Reading sources task started...")
    await scrape_adidas()
    await scrape_carhartt()
    await scrape_converse()
    await scrape_nike()
