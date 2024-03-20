import asyncio
import json
import re

from bs4 import BeautifulSoup

test_file = "src/web_sources/adidas/test-files/thirdchunk-bingo.html"


async def test_parse_page():
    # Load the HTML content from the file
    with open(test_file, "r", encoding="utf-8") as file:
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

    # Find the script tag containing 'window.DATA_STORE'
    for script_tag in soup.find_all("script"):
        if "window.DATA_STORE" in script_tag.text:
            # Extract the JSON string using regular expressions
            json_string_match = re.search(
                r"window.DATA_STORE = JSON.parse\((.*)\);", script_tag.string
            )
            if json_string_match:
                json_string = json_string_match.group(1)
                # The JSON string is double encoded, so decode it twice
                data_store = json.loads(json.loads(json_string))

                # verify the structure of data_store
                print(data_store.keys())  # Check the top-level keys

                """ # Directly write json_string to a file for inspection
                async with aiofiles.open("data_store_raw.json", "w") as file:
                    await file.write(json_string)

                # Decode JSON string and write pretty JSON to another file
                decoded_json = json.loads(json.loads(json_string))
                async with aiofiles.open("data_store_pretty.json", "w") as file:
                    await file.write(json.dumps(decoded_json, indent=4))
                """
                # Access "itemList" and "items" within the data_store
                item_list = data_store["plp"].get("itemList", {})
                items = item_list.get("items", [])
                print(len(items))
                # Process each item as needed
                for item in items:
                    # Example: print item's 'link' and 'salePrice'
                    print(
                        f"Link: {item.get('link')}, Sale Price: {item.get('salePrice')}"
                    )

                return items  # Return the items list for further processing
            break  # Exit loop after finding the correct script tag

        """ products.append(
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
        ) """
    return products


# Run the test
if __name__ == "__main__":
    asyncio.run(test_parse_page())
