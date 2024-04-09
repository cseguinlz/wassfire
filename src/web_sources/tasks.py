from src.web_sources.adidas.adidas import scrape_adidas
from src.web_sources.carhartt.carhartt import scrape_carhartt
from src.web_sources.converse.converse import scrape_converse
from src.web_sources.nike.nike import scrape_nike


async def read_sources_task():
    await scrape_adidas()
    await scrape_carhartt()
    await scrape_converse()
    await scrape_nike()
