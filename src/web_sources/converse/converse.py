import re
from datetime import datetime

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from src.products import service
from src.utils import setup_logger
from src.web_sources.converse.urls import CONVERSE_BASE_OUTLET_URLS
from src.web_sources.utils import (
    categorize_product,
    construct_full_product_link,
    encode_url,
    fetch_converse_products_page,
    parse_float,
)

logger = setup_logger(__name__)
BRAND = "Converse"
SOURCE_NAME = "converse"
SOURCE_ID: int = 3


async def scrape_converse(db: AsyncSession):
    for entry in CONVERSE_BASE_OUTLET_URLS:
        country_code = entry["hreflang"]
        base_url = entry["url"]
        encoded_base_url = encode_url(base_url)
        await scrape_and_save_products(encoded_base_url, country_code, db)
    logger.info("********* Converse read ✅ *************")


async def scrape_and_save_products(url: str, country_code: str, db: AsyncSession):
    start = 0  # Starting index of the products you want to fetch
    size = 60  # Max Number of products to fetch
    max_start = 180
    while start <= max_start:
        response = await fetch_converse_products_page(url, start, size, country_code)
        # Only for testing purpuses
        # await write_response_to_file(response.text, "test_converse_response.html")
        if response.status_code == 200:
            products = await parse_converse_page(response.text, country_code)
            logger.info(f"Parsed {len(products)} products")
            for product_data in products:
                await service.create_or_update_product(
                    db=db, product_data=product_data, source_name=SOURCE_NAME
                )  # Save each product
            logger.info(
                f"Saved {len(products)} products for {BRAND} in {country_code}."
            )
            start += size
        else:
            logger.info(f"Failed with status code: {response.status_code}")
            logger.error(
                f"Failed to fetch page: {url} with status code: {response.status_code}"
            )
            start += size
            return 0, 0


# Mappings based on known patterns in the text.
category_mapping = {
    "Zapatillas": "Sneakers",
    "Camiseta": "T-Shirt",
    "Chaqueta": "Jacket",
    "Skate": "Skate Shoes",
}


async def parse_converse_page(html_content: str, country_code: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    for product_tile in soup.select(".plp-grid__item"):
        name_section = product_tile.select_one(".product-tile__img-url")
        name = name_section["title"] if name_section else "No Name Found"

        # Categorization based on name and description
        badge_text = product_tile.select_one(".product-tile__secondary-badge")
        description = badge_text.text.strip() if badge_text else ""
        combined_description = f"{name} {description}"
        category_info = categorize_product(combined_description)
        logger.debug(f"Categories: {category_info}")

        # Initialize category
        category = ""
        # Extracting Category
        for keyword, mapped_category in category_mapping.items():
            if re.search(keyword, description, re.IGNORECASE):
                category = mapped_category
                break

        product_link = name_section["href"] if name_section else ""
        product_url = construct_full_product_link(
            SOURCE_NAME, country_code, product_link
        )
        # logger.debug(f"Product url {SOURCE_NAME}: {product_url}")
        # For image URL, the main image is what we want
        image_url_data = product_tile.select_one("img[data-src]")
        image_url = image_url_data["data-src"] if image_url_data else ""
        # Extracting pricing information
        pricing_info = product_tile.select_one(".product-tile__pricing")
        if pricing_info:
            sale_price_element = pricing_info.select_one(".product-price--sales")
            original_price_element = pricing_info.select_one(".product-price--standard")
            price_range_element = pricing_info.select_one(".product-price--range")

            # Handle price range
            if price_range_element:
                price_range_text = price_range_element.text.strip()
                sale_price_matches = re.findall(r"\d+,\d+", price_range_text)
                if sale_price_matches:
                    # Assuming we take the lower price from the range
                    sale_price_text = sale_price_matches[0].replace(",", ".")
                    sale_price = parse_float(sale_price_text, default=0.0)
                else:
                    sale_price = 0.0
                original_price = (
                    sale_price  # Assuming the lower price as the only price
                )
                discount_percentage = (
                    0.0  # No discount percentage calculation for ranges
                )
            # Handle single price
            elif sale_price_element and original_price_element:
                sale_price_text = sale_price_element.text.strip().split("\n")[0]
                sale_price_matches = re.findall(r"\d+,\d+", sale_price_text)
                if sale_price_matches:
                    sale_price_text = sale_price_matches[0].replace(",", ".")
                    sale_price = parse_float(sale_price_text, default=0.0)
                else:
                    sale_price = 0.0

                # Extract the original price text directly
                original_price_text = pricing_info.select_one(
                    ".product-price--standard"
                ).text.strip()
                original_price = parse_float(
                    re.sub("[^0-9,]", "", original_price_text).replace(",", ".")
                )

                if original_price > 0 and sale_price > 0:
                    discount_percentage = round((1 - (sale_price / original_price)), 2)
                else:
                    discount_percentage = 0.0
        else:
            sale_price = 0.0
            original_price = 0.0
            discount_percentage = 0.0

        # Color variations are simplified in this example, extracted from data attribute
        color_variations = product_tile.get("data-colors-to-show", "").split("/")

        products.append(
            {
                "source_id": SOURCE_ID,  # Adjust based on actual source ID system
                "name": name,
                "description": description,
                "country_lang": country_code,
                "brand": "Converse",
                "section": category_info["section"],
                "category": category,
                "type": category_info["sport"],
                "color": ", ".join(color_variations),
                "product_link": product_url,
                "image_url": image_url,
                "original_price": original_price,
                "sale_price": sale_price,
                "discount_percentage": discount_percentage,
                "source_published_at": datetime.now(),
            }
        )

    return products
