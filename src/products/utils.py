import httpx

from src.utils import setup_logger
from src.web_sources.utils import get_common_headers

logger = setup_logger(__name__)


async def is_product_available(product_url, product_brand, image_url):
    headers = get_common_headers(product_url, f"{product_brand}.com")
    try:
        async with httpx.AsyncClient() as client:
            # First try to fetch the main product page
            response = await client.get(
                product_url, headers=headers, follow_redirects=True
            )
            if 200 <= response.status_code < 400:
                return True
            elif response.status_code == 403:
                # If forbidden, try fetching the image URL as a fallback
                image_response = await client.get(
                    image_url, headers=headers, follow_redirects=True
                )
                return 200 <= image_response.status_code < 400
            else:
                return False
    except httpx.RequestError as e:
        logger.error(
            f"Request error when checking product availability for {product_url}: {str(e)}"
        )
        return False
    except httpx.HTTPStatusError as e:
        # Handle cases where the server returns a status code that is not considered successful
        logger.error(
            f"HTTP status error when checking product availability for {product_url}: {str(e)}"
        )
        return False
