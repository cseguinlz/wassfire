import asyncio
import json

from bs4 import BeautifulSoup

from src.utils import setup_logger
from src.web_sources.utils import fetch_page

logger = setup_logger(__name__)


async def extract_json_data(url: str):
    """Extracts JSON data from the script tag of the fetched page."""
    response = await fetch_page(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find(
            "script", attrs={"type": "application/json", "data-mf-id": "header-mf"}
        )
        if script_tag:
            json_data = json.loads(
                script_tag.string
            )  # Use .string to get the content of the tag
            return json_data
    else:
        logger.debug(f"Failed to fetch the page: Status code {response.status_code}")
    return None


async def parse_category_links_from_flyout(flyout_node, base_url: str):
    """Parses category links from the 'flyout' node."""
    category_links = []
    if flyout_node:
        for column in flyout_node.get("columns", []):
            section = column["topLink"]["title"]
            for item in column.get("items", []):
                category = item["title"]
                category_url = f"{base_url}{item['url']}"
                category_links.append(
                    {
                        "section": section,
                        "category": category,
                        "url": category_url,
                    }
                )
    return category_links


async def generate_urls(url: str, base_url: str):
    """Integrates fetching, searching, and parsing into a single workflow."""
    json_data = await extract_json_data(url)

    relevant_flyout_node = json_data["desktopData"][6]
    if not relevant_flyout_node:
        logger.debug("Relevant flyout node not found.")
        return []

    return await parse_category_links_from_flyout(relevant_flyout_node, base_url)


async def main():
    url = "https://www.adidas.pt/outlet"
    base_url = "https://www.adidas.pt"
    category_links = await generate_urls(url, base_url)
    for link in category_links:
        logger.debug(link)


if __name__ == "__main__":
    asyncio.run(main())
