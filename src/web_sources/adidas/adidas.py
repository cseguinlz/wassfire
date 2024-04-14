# adidas.py

import json
import math
import re
from datetime import datetime

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from src.products import service
from src.utils import setup_logger
from src.web_sources.adidas.urls import ADIDAS_BASE_OUTLET_URLS
from src.web_sources.utils import (
    construct_full_product_link,
    encode_url,
    fetch_page,
    parse_float,
    parse_percentage,
)

logger = setup_logger(__name__)

BRAND = "Adidas"
SOURCE_NAME = "adidas"
SOURCE_ID: int = 1


async def parse_page(html_content: str, country_code: str, section: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []
    total_count = 0
    view_size = 0

    # Find and process the script tag containing 'window.DATA_STORE'
    for script_tag in soup.find_all("script"):
        if "window.DATA_STORE" in script_tag.text:
            json_string_match = re.search(
                r"window.DATA_STORE = JSON.parse\((.*)\);", script_tag.string
            )
            if json_string_match:
                json_string = json_string_match.group(1)
                data_store = json.loads(json.loads(json_string))
                # Debugging only
                # await write_response_to_file(data_store, "outlet.json")
                plp_data = data_store.get("plp", {})
                item_list_data = plp_data.get("itemList", {})
                item_list = item_list_data.get("items", [])
                total_count = item_list_data.get("count", 0)
                view_size = item_list_data.get("viewSize", 0)

                for item in item_list:
                    discount_percentage = parse_percentage(
                        item.get("salePercentage", "")
                    )
                    # get centered image:
                    images = item.get("images", [])
                    side_lateral_center_view_url = find_image_with_view(
                        images, "Side Lateral Center View"
                    )
                    # Fallback to using items.image.src if side_lateral_center_view_url is empty
                    if (
                        not side_lateral_center_view_url
                        and item.get("image")
                        and item.get("image").get("src")
                    ):
                        side_lateral_center_view_url = item["image"]["src"]

                    full_product_link = construct_full_product_link(
                        SOURCE_NAME, country_code, item.get("link", "")
                    )
                    # logger.debug(f"Product url {SOURCE_NAME}: {full_product_link}")

                    category = item.get("category", "")
                    type = item.get("sport", "")
                    description = item.get("altText", "")
                    products.append(
                        {
                            "source_id": SOURCE_ID,
                            "name": description,
                            "description": description,
                            "country_lang": country_code,
                            "brand": BRAND,
                            "section": section,
                            "category": category,
                            "type": type,
                            "color": "",  # NO color, only custom code: "colorVariations": ["HP5522", "HP5523"],
                            "discount_percentage": discount_percentage,
                            "original_price": parse_float(item.get("price", "")),
                            "sale_price": parse_float(item.get("salePrice", "")),
                            "product_link": f"{full_product_link}",
                            "image_url": side_lateral_center_view_url,
                            "second_image_url": item.get("secondImage", {}).get(
                                "src", ""
                            ),
                            "source_published_at": datetime.fromisoformat(
                                item.get("onlineFrom", "").rstrip("Z")
                            ),
                        }
                    )
                break  # Exit after processing the correct script tag

    return products, total_count, view_size


async def scrape_and_save_products(
    url: str, country_code: str, section: str, category: str, db: AsyncSession
):
    response = await fetch_page(
        url,
        "www.adidas.com",
    )
    if response.status_code == 200:
        products, total_count, view_size = await parse_page(
            response.text, country_code, section.lower()
        )
        for product_data in products:
            await service.create_or_update_product(
                db=db, product_data=product_data, source_name=SOURCE_NAME
            )  # Save each product
        logger.info(
            f"Saved {len(products)} products for {section}-{category} in {country_code}."
        )

        # Your existing logic to handle products...
        return total_count, view_size
    else:
        logger.info(f"Failed with status code: {response.status_code}")
        logger.error(
            f"Failed to fetch page: {url} with status code: {response.status_code}"
        )
        return 0, 0


async def scrape_adidas(db: AsyncSession, start: int = 0):
    for entry in ADIDAS_BASE_OUTLET_URLS:
        country_code = entry["hreflang"]
        for category in entry.get("category_url", []):
            base_url = category["url"]
            encoded_base_url = encode_url(base_url)
            paginated_url = (
                f"{encoded_base_url}?start={start}" if start > 0 else base_url
            )
            total_count, view_size = await scrape_and_save_products(
                paginated_url,
                country_code,
                category["section"],
                category["category"],
                db,
            )

            if total_count > 0 and view_size > 0:
                total_pages = math.ceil(total_count / view_size)
                for page in range(1, total_pages):
                    start_param = page * view_size
                    next_page_url = f"{encoded_base_url}?start={start_param}"
                    await scrape_and_save_products(
                        next_page_url,
                        country_code,
                        category["section"],
                        category["category"],
                        db,
                    )
    logger.info("********* Adidas read ✅ *************")


def find_image_with_view(images, view_name):
    """
    Get centered image
    """
    for image in images:
        if image.get("metadata", {}).get("view") == view_name:
            return image.get("src")
    return None
