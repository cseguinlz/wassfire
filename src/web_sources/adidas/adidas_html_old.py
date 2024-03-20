from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Product
from src.products import service
from src.utils import convert_price_to_float, setup_logger
from src.web_sources.adidas.urls import ADIDAS_BASE_OUTLET_URLS
from src.web_sources.utils import encode_url, fetch_page

logger = setup_logger(__name__)

BRAND = "adidas"


async def parse_page(html_content: str, country_code: str, section: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    for product_div in soup.select(".glass-product-card"):
        name_element = product_div.select_one('[data-auto-id="product-card-title"]')
        logger.debug(f"Parsing product: {name_element}")
        category_element = product_div.select_one(
            '[data-auto-id="product-card-category"]'
        )
        color_variations_element = product_div.select_one(
            '[data-auto-id="product-card-colvar-count"]'
        )
        product_link_element = product_div.select_one(
            '[data-auto-id="glass-hockeycard-link"]'
        )
        image_container = product_div.select_one(".glass-product-card__assets-link img")
        discount_element = product_div.select_one(".discount-badge___318Q7")
        price_elements = product_div.select(".gl-price-item")

        # Skipping products without discount or missing product link
        if not discount_element or not product_link_element:
            continue

        original_price = sale_price = None
        if price_elements:
            original_price = await convert_price_to_float(price_elements[0].text)
            sale_price = await convert_price_to_float(price_elements[-1].text)

        product_link = product_link_element["href"] if product_link_element else "N/A"

        products.append(
            {
                "name": name_element.text.strip() if name_element else "N/A",
                "country_lang": country_code,
                "brand": BRAND,
                "section": section,
                "category": category_element.text.strip()
                if category_element
                else "N/A",
                "color_variations": color_variations_element.text.strip()
                if color_variations_element
                else "N/A",
                "discount_percentage": discount_element.text.strip()
                if discount_element
                else None,
                "original_price": original_price,
                "sale_price": sale_price,
                "product_link": product_link,
                "image_url": image_container["src"] if image_container else "N/A",
            }
        )
    return products


async def check_duplicate_product(db: AsyncSession, product_link: str) -> bool:
    """Check if a product with the given link already exists in the database."""
    result = await db.execute(select(Product).filter_by(product_link=product_link))
    return result.scalars().first() is not None


async def scrape_and_save_products(
    url: str, country_code: str, section: str, db: AsyncSession
):
    # Encode the URL
    encoded_url = encode_url(url)
    print(f"Scraping for url {encoded_url}...")
    response = await fetch_page(encoded_url)
    if response.status_code == 200:
        products = await parse_page(response.text, country_code, section)
        for product_data in products:
            # Check for duplicate before attempting to create a new product
            if await check_duplicate_product(db, product_data["product_link"]):
                print(f"Skipping duplicate product: {product_data['product_link']}")
                continue
            await service.create_or_update_product(
                db=db, product_data=product_data, source_name="adidas"
            )  # Save each product
        print(f"Saved {len(products)} products for {country_code}.")
    else:
        print(f"Failed with status code: {response.status_code}")


async def scrape_adidas(db: AsyncSession):
    for entry in ADIDAS_BASE_OUTLET_URLS:
        country_code = entry["hreflang"]
        print(f"Scraping for country {country_code}...")
        for category in entry.get("category_url", []):
            await scrape_and_save_products(
                category["url"], country_code, category["section"], db
            )
