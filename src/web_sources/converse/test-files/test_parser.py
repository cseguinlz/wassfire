import asyncio
import re
from datetime import datetime

from bs4 import BeautifulSoup

from src.web_sources.utils import parse_float

# Mappings based on known patterns in the text.
section_mapping = {
    "Unisex": "Unisex",
    "Hombre": "Men",
    "Mujer": "Women",
    "Infantil": "Kids",
}

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
        product_link = name_section["href"] if name_section else ""

        # For image URL, assuming the main image is what we want
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

        print(
            f"Sale price: {sale_price} €, Original price: {original_price} €, Discount: {discount_percentage}%"
        )

        # Color variations are simplified in this example, extracted from data attribute
        color_variations = product_tile.get("data-colors-to-show", "").split("/")

        # Extracting section and category
        badge_text = product_tile.select_one(".product-tile__secondary-badge")
        text = badge_text.text.strip() if badge_text else ""
        section = "Unknown"
        category = "Unknown"
        for keyword, mapped_section in section_mapping.items():
            if re.search(keyword, text, re.IGNORECASE):
                section = mapped_section
                break
        for keyword, mapped_category in category_mapping.items():
            if re.search(keyword, text, re.IGNORECASE):
                category = mapped_category
                break

        # Placeholder URLs and other informationg
        short_url = "wass.promo/something"

        products.append(
            {
                "source_id": "Converse",  # Adjust based on actual source ID system
                "name": name,
                "country_lang": country_code,
                "brand": "Converse",
                "section": section,
                "category": category,
                "color": ", ".join(color_variations),
                "product_link": product_link,
                "short_url": short_url,
                "image_url": image_url,
                "original_price": original_price,
                "sale_price": sale_price,
                "discount_percentage": discount_percentage,
                "source_published_at": datetime.now().isoformat(),
            }
        )

    return products


async def main():
    # Load HTML content from a file (for testing purposes)
    with open(
        "src/web_sources/converse/test-files/product_list.html", "r", encoding="utf-8"
    ) as file:
        html_content = file.read()

    country_code = "PT"  # Example country code
    products = await parse_converse_page(html_content, country_code)
    for product in products:
        print(product)


if __name__ == "__main__":
    asyncio.run(main())
