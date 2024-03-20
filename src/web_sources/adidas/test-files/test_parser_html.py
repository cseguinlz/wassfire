import asyncio

from bs4 import BeautifulSoup


async def test_parse_page():
    # Load the HTML content from the file
    with open("adidas_calzado_hombre_outlet.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Call your parse_page function
    country_code = "test_country"
    section = "test_section"
    products = await parse_page(html_content, country_code, section)
    print(len(products))
    # Print the results for inspection
    """ for product in products:
        print(product)
 """


async def parse_page(html_content: str, country_code: str, section: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []
    counter = 0
    for product_div in soup.select(".glass-product-card"):
        name_element = product_div.select_one('[data-auto-id="product-card-title"]')
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
        print(name_element)
        print(price_elements)

        if price_elements:
            counter += 1

        print(counter)

        # Revised price extraction logic
        if price_elements:
            if len(price_elements) == 2:
                original_price_str = (
                    price_elements[0].text.strip().replace("€", "").replace(",", ".")
                )
                sale_price_str = (
                    price_elements[1].text.strip().replace("€", "").replace(",", ".")
                )
            elif len(price_elements) == 1:
                original_price_str = sale_price_str = (
                    price_elements[0].text.strip().replace("€", "").replace(",", ".")
                )
            else:
                original_price_str = sale_price_str = None
        else:
            original_price_str = sale_price_str = None

        # Conversion to float with error handling
        def convert_price_to_float(price_str):
            if price_str is None:
                return None
            try:
                # Attempt to remove currency symbols and convert to float
                no_currency = (
                    price_str.replace("€", "")
                    .replace("$", "")
                    .replace("£", "")
                    .replace(",", ".")
                )
                return float(no_currency)
            except ValueError:
                # Return None if conversion fails
                return None

        original_price = convert_price_to_float(original_price_str)
        sale_price = convert_price_to_float(sale_price_str)

        products.append(
            {
                "name": name_element.text.strip() if name_element else "N/A",
                "country_lang": country_code,
                "brand": "BRAND",
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
                "product_link": product_link_element["href"]
                if product_link_element
                else "N/A",
                "image_url": image_container["src"] if image_container else "N/A",
            }
        )

    return products


# Run the test
if __name__ == "__main__":
    asyncio.run(test_parse_page())
