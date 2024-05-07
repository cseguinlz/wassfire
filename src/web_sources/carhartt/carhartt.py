import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from src.products import service
from src.utils import setup_logger
from src.web_sources.carhartt.urls import CARHARTT_BASE_OUTLET_URLS
from src.web_sources.utils import (
    categorize_product,
    construct_full_product_link,
    encode_url,
    fetch_ajax_carhartt_content,
    parse_float,
)

logger = setup_logger(__name__)

BRAND = "Carhartt"
SOURCE_NAME = "carhartt"
SOURCE_ID: int = 2  # Example ID, should be unique


async def scrape_carhartt(db: AsyncSession):
    for entry in CARHARTT_BASE_OUTLET_URLS:
        country_code = entry["hreflang"]
        base_url = entry["url"]
        encoded_base_url = encode_url(base_url)
        await scrape_and_save_products(encoded_base_url, country_code, db)
    logger.info("********* Carhartt read ✅ *************")


async def scrape_and_save_products(url: str, country_code: str, db: AsyncSession):
    response = await fetch_ajax_carhartt_content(url)
    # Only for testing purpuses
    # await write_response_to_file(response.text, "test_carhartt_response.html")
    if response.status_code == 200:
        products = await parse_page(response.text, country_code)
        logger.info(f"Parsed {len(products)} products")
        for product_data in products:
            await service.create_or_update_product(
                db=db, product_data=product_data, source_name=SOURCE_NAME
            )  # Save each product
        logger.info(f"Saved {len(products)} products for {BRAND} in {country_code}.")
    else:
        logger.info(f"Failed with status code: {response.status_code}")
        logger.error(
            f"Failed to fetch page: {url} with status code: {response.status_code}"
        )
        return 0, 0


async def parse_page(html_content: str, country_code: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    for product_cell in soup.select(".product-cell"):
        product_link_tag = product_cell.find(
            "a", id=re.compile("^catalogEntry_imgOUT_")
        )
        if product_link_tag:
            product_link = construct_full_product_link(
                SOURCE_NAME, country_code, product_link_tag["href"]
            )
        logger.debug(f"Product link {SOURCE_NAME}: {product_link}")
        name = product_cell.select_one(".product-description h5").text.strip()
        # Try to find categories
        category_info = categorize_product(name)
        # logger.debug(f"Categories: {category_info}")

        image_url = product_cell.select_one(".product-cell-image img.front")["src"]
        price_data = product_cell.select_one(".price span")
        original_price_tag = product_cell.select_one("del")
        if not original_price_tag:
            continue  # Skip products without a crossed-out original price
        original_price = original_price_tag.text.strip()
        sale_price = price_data.text.strip().split("\n")[0]

        # Parsing price to float
        original_price_float = parse_float(
            re.sub("[^0-9,]", "", original_price).replace(",", ".")
        )
        sale_price_float = parse_float(
            re.sub("[^0-9,]", "", sale_price).replace(",", ".")
        )
        discount_percentage = (
            (Decimal("1") - (Decimal(sale_price_float) / Decimal(original_price_float)))
            if original_price_float
            else Decimal("0")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Capturing color variations
        color_variations = [
            li.find("a")["title"]
            for li in product_cell.select(
                ".color-swatches-overlay .product-cell-swatches li"
            )
        ]
        products.append(
            {
                "source_id": SOURCE_ID,
                "name": name,
                "country_lang": country_code,
                "brand": BRAND,
                "section": category_info[
                    "section"
                ],  # Section is not defined in the HTML
                "category": "",  # Similarly, category is not directly available
                "type": category_info[
                    "sport"
                ],  # Type information is also not available in the HTML snippet
                "color": ", ".join(color_variations),
                "discount_percentage": discount_percentage,
                "original_price": original_price_float,
                "sale_price": sale_price_float,
                "product_link": product_link,
                "image_url": image_url,
                "second_image_url": "",  # Second image URL extraction logic needs adaptation if available
                "source_published_at": datetime.now(),  # Placeholder for actual published date if available
            }
        )

    return products
