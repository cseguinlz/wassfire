import base64
from urllib.parse import quote

import aiofiles
import httpx
from curl_cffi.requests import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.models import Product
from src.utils import setup_logger
from src.web_sources.config import BASE_URL_MAPPING

logger = setup_logger(__name__)


# Common headers used for HTTP requests
def get_common_headers(url: str, authority: str):
    """
    Generates common headers with a dynamic authority.

    Parameters:
    - authority (str): The authority value to be set in the headers.

    Returns:
    - dict: A dictionary of common headers with the specified authority.
    """
    common_headers = {
        "authority": authority,
        "accept": "application/json, text/plain, */*",
        "Origin": url,
        "Referer": url,
        "accept-language": "en-US,en;q=0.9,es;q=0.8",
        "dnt": "1",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Sec-Gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    return common_headers


async def check_duplicate_product(db: AsyncSession, product_link: str) -> bool:
    """Check if a product with the given link already exists in the database."""
    result = await db.execute(select(Product).filter_by(product_link=product_link))
    return result.scalars().first() is not None


async def fetch_page(url: str, authority: str, headers=None):
    """
    Fetches a webpage's content.

    :param url: URL of the webpage to fetch.
    :param headers: Optional headers to use for the request. If None, COMMON_HEADERS are used.
    :return: The HTTP response.
    """
    if headers is None:
        if headers is None:
            headers = get_common_headers(url, authority)
    async with AsyncSession() as session:
        response = await session.get(url, headers=headers)
        return response


def encode_url(url: str, safe_chars: str = "/:") -> str:
    """
    Encodes a URL, making it safe for requests.

    Args:
        url (str): The original URL to be encoded.
        safe_chars (str, optional): Characters that should not be encoded.

    Returns:
        str: The encoded URL.
    """
    return quote(url, safe=safe_chars)


"""
Safely parse floats
Used for pricing fields
"""


def parse_float(price_str, default=None):
    try:
        return float(price_str)
    except ValueError:
        return default


def parse_percentage(percentage_str):
    """
    Convert a percentage string to a decimal float.

    :param percentage_str: String representation of the percentage, e.g., "55%"
    :return: Decimal representation of the percentage, e.g., 0.55
    """
    try:
        # Remove the '%' character and convert to float, then divide by 100
        return float(percentage_str.strip("%")) / 100
    except ValueError:
        # Return None or 0 if the string cannot be converted
        return None


def get_full_product_link(country_lang, product_link):
    base_url = BASE_URL_MAPPING.get(
        country_lang, "https://www.adidas.com"
    )  # Default to .com if not found
    if not product_link:
        # in case no link, at least we show up as a traffic source and give something to the user
        return f"{base_url}/outlet"

    return f"{base_url}{product_link}{settings.LEAD_SOURCE}"


async def write_response_to_file(response_text, filename="response.html"):
    # Use aiofiles to write the response text to a file asynchronously
    async with aiofiles.open(filename, mode="w") as file:
        await file.write(response_text)


async def fetch_ajax_carhartt_content(url: str):
    params = {
        "ajaxStoreImageDir": "/wcsstore/CarharttEMEASAS/",
        "categoryId": "3074457345616696173",
        "resultsPerPage": "100",
        "sType": "SimpleSearch",
        "catalogId": "3074457345616677219",
        "langId": "-5",
        "contractId": "4000000000000000003",
        "ajaxStoreDir": "/CarharttEMEASAS/",
        "ddkey": "AjaxProductListingView",
        "storeId": "715838034",
        "contentBeginIndex": "0",
        "productBeginIndex": "0",
        "beginIndex": "0",
        "orderBy": "6",
        "pageView": "categoryListPage",
        "resultType": "both",
        "pageSize": "100",
    }
    headers = get_common_headers(url, "www.carhartt.com")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        return response


async def fetch_converse_products_page(
    url: str, start: int, size: int, country_code: str
):
    """
    Fetches a page of products from the Converse website using AJAX-like request.

    :param url: Base URL for the AJAX request.
    :param start: The starting index of products to fetch.
    :param size: Number of products to fetch. Máx 60 per call.
    :param headers: Optional custom headers for the request.
    :return: The HTTP response text containing the product listing.
    """
    # Update the URL with the query parameters for pagination
    params = {
        "lang": {country_code},
        "srule": "top-sellers",
        "start": {start},
        "sz": {size},
        "format": "page-element",
        "interrupterSize": 0,
    }
    # Use common headers if none are provided
    headers = get_common_headers(url, "www.converse.com")

    async with AsyncSession() as session:
        response = await session.get(url, params=params, headers=headers)
        return response


async def get_base64_image(url):
    headers = get_common_headers(url, "www.converse.com")

    async with AsyncSession() as session:
        response = await session.get(url, headers=headers)
    if response.status_code == 200:
        # Convert the binary content to a base64-encoded string
        return base64.b64encode(response.content).decode("utf-8")
    else:
        return None


def get_nike_params(anchor, count, country_code, lang):
    return {
        "queryid": "products",
        "anonymousId": "B229650DD47D6D94D6EF3C40AEDB9815",
        "country": country_code,  # "pt"
        "endpoint": f"/product_feed/rollup_threads/v2?filter=marketplace(PT)&filter=language(pt-PT)&filter=employeePrice(true)&filter=attributeIds(5b21a62a-0503-400c-8336-3ccfbff2a684)&anchor={anchor}&consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647&count={count}&sort=effectiveStartViewDateDesc",
        "language": lang,  # "pt-PT"
        "localizedRangeStr": "{lowestPrice} — {highestPrice}",
    }


async def fetch_nike_products_page(url, anchor, count, country_code, lang):
    """
    Fetches a page of Nike products.

    :param url: The base URL for the Nike API request.
    :param anchor: The pagination anchor.
    :param count: The number of products to fetch.
    :return: JSON response containing product information.
    """
    headers = get_common_headers(
        "https://www.nike.com",
        "api.nike.com",
    )
    params = get_nike_params(anchor, count, country_code, lang)

    # Manually build the full URL for logging/debugging
    # full_url = f"{url}?{urlencode(params)}"
    # print(f"Requesting URL: {full_url}")

    async with AsyncSession() as session:
        response = await session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            # json_response = response.json()
            # print(json_response)  # Print the JSON response
            # return json_response
            return response.json()  # Return the JSON response
        else:
            logger.debug(f"Failed to fetch products: HTTP {response.status_code}")
            return None


"""

# Test: run `python src/web_sources/utils.py`
or as a module:
`python -m src.web_sources.utils`

async def main():
    url = "https://www.adidas.es/calzado-hombre-outlet"
    page_content = await fetch_page(url)
    with open("response_content.html", "w", encoding="utf-8") as file:
        file.write(page_content.text)


if __name__ == "__main__":
    asyncio.run(main())



async def main():
    content = await fetch_ajax_carhartt_content()
    with open("ajax_response.html", "w") as file:
        file.write(content)


if __name__ == "__main__":
    asyncio.run(main())
"""
