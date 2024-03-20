from urllib.parse import quote

from curl_cffi.requests import AsyncSession

from src.config import settings
from src.web_sources.config import BASE_URL_MAPPING

# Common headers used for HTTP requests
COMMON_HEADERS = {
    "authority": "www.adidas.es",
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


"""

# Test: run python src/web_sources/utils.py

async def main():
    url = "https://www.adidas.es/calzado-hombre-outlet"
    page_content = await fetch_page(url)
    with open("response_content.html", "w", encoding="utf-8") as file:
        file.write(page_content.text)


if __name__ == "__main__":
    asyncio.run(main())
"""
