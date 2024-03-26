from urllib.parse import quote

import aiofiles
import httpx
from curl_cffi.requests import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.models import Product
from src.web_sources.config import BASE_URL_MAPPING

# Common headers used for HTTP requests
COMMON_HEADERS = {
    "authority": "www.adidas.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,es;q=0.8",
    "dnt": "1",
    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


async def check_duplicate_product(db: AsyncSession, product_link: str) -> bool:
    """Check if a product with the given link already exists in the database."""
    result = await db.execute(select(Product).filter_by(product_link=product_link))
    return result.scalars().first() is not None


async def fetch_page(url: str, headers=None):
    """
    Fetches a webpage's content.

    :param url: URL of the webpage to fetch.
    :param headers: Optional headers to use for the request. If None, COMMON_HEADERS are used.
    :return: The HTTP response.
    """
    if headers is None:
        if headers is None:
            headers = COMMON_HEADERS.copy()
            # Set the referer header dynamically based on the URL
            headers["Referer"] = url
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
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "es;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.carhartt.com",
        "Referer": "https://www.carhartt.com/es/es-es/categoria/rebajas",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        return response


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
