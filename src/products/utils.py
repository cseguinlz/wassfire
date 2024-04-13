import httpx

from src.utils import setup_logger
from src.web_sources.utils import get_common_headers

logger = setup_logger(__name__)


async def is_product_available(product_url, product_brand):
    headers = get_common_headers(product_url, f"{product_brand}.com")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                product_url, headers=headers, follow_redirects=True
            )
            # Checking for a range of success status codes
            return 200 <= response.status_code < 400
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
