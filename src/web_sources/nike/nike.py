from sqlalchemy.ext.asyncio import AsyncSession

from src.products import service
from src.utils import setup_logger
from src.web_sources.nike.urls import NIKE_BASE_OUTLET_URLS
from src.web_sources.utils import (
    encode_url,
    fetch_nike_products_page,
    parse_float,
)

logger = setup_logger(__name__)
BRAND = "Nike"
SOURCE_NAME = "nike"
SOURCE_ID: int = 4
BASE_URL = "https://www.nike.com/"


async def scrape_nike(db: AsyncSession):
    for entry in NIKE_BASE_OUTLET_URLS:
        country_lang = entry["hreflang"]
        base_url = entry["url"]
        encoded_base_url = encode_url(base_url)
        await scrape_and_save_products(encoded_base_url, country_lang, db)


async def scrape_and_save_products(url: str, country_lang: str, db: AsyncSession):
    country_code = country_lang.split("-")[0]
    anchor = 0  # Starting index of the products you want to fetch
    count = 60  # Max Number of products to fetch
    while True:
        products_json = await fetch_nike_products_page(
            url, anchor, count, country_code, country_lang
        )
        if (
            not products_json
            or "data" not in products_json
            or "products" not in products_json["data"]
            or not products_json["data"]["products"].get("products")
        ):
            logger.info("nothing here")
            break  # Exit loop if no products are returned
        products = await parse_nike_products(products_json, country_lang)
        logger.info(f"Parsed {len(products)} products")
        for product_data in products:
            await service.create_or_update_product(
                db=db, product_data=product_data, source_name=SOURCE_NAME
            )  # Save each product
            logger.info(
                f"Saved {len(products)} products for {BRAND} in {country_code}."
            )
        anchor += count  # Adjust anchor param for next iteration


async def parse_nike_products(json_data, country_lang):
    products = []
    data = json_data.get("data", {})
    products_data = data.get("products", {}).get("products", [])
    # logger.info(f"in parse_nike, data: {products_data}")
    for product in products_data:
        title = product.get("title", "")
        description = product.get("subtitle", "")
        category = product.get("productType", "")

        product_url = format_product_url(
            product.get("url", ""), country_lang.split("-")[0]
        )

        price_info = product.get("price", {})
        if price_info:
            current_price = parse_float(price_info.get("currentPrice", ""))
            full_price = parse_float(price_info.get("fullPrice", ""))
            if current_price > 0 and full_price > 0:
                discount_percentage = round((1 - (current_price / full_price)), 2)
            else:
                discount_percentage = 0.0
        else:
            current_price = 0.0
            full_price = 0.0
            discount_percentage = 0.0

        color_description_raw = product.get("colorDescription")
        if color_description_raw is None:
            color_description = ""
        else:
            color_descriptions = color_description_raw.split("/")
            color_description = ", ".join(color_descriptions)
        squarish_url = product.get("images", {}).get("squarishURL", "")
        product_details = {
            "source_id": SOURCE_ID,
            "name": title,
            "description": description,
            "country_lang": country_lang,
            "brand": BRAND,
            "section": "",
            "category": category,
            "type": "",
            "color": color_description,
            "discount_percentage": discount_percentage,
            "original_price": full_price,
            "sale_price": current_price,
            "product_link": product_url,
            "image_url": squarish_url,
        }
        products.append(product_details)

    return products


def format_product_url(product_url, country_lang="en"):
    if "{countryLang}" in product_url:
        product_url = product_url.replace("{countryLang}", country_lang)
    full_url = f"{BASE_URL}{product_url}"
    return full_url
