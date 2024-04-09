# src/utils.py or create a new src/url_shortener.py


import httpx

from src.config import settings
from src.utils import setup_logger  # Import your settings

logger = setup_logger(__name__)


async def shorten_url_with_tly(long_url: str, description: str, tags: list[str]) -> str:
    async with httpx.AsyncClient() as client:
        tags_ids = await get_tags_ids(tags, client)  # Pass the client to get_tags_ids

        payload = {
            "long_url": long_url,
            "domain": settings.T_LY_DOMAIN,
            "description": description,
            "tags": tags_ids,
        }
        headers = {
            "Authorization": f"Bearer {settings.T_LY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = await client.post(
            settings.T_LY_LINK_URL, json=payload, headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("short_url")
        else:
            raise Exception(
                f"Failed to shorten URL. Status code: {response.status_code}, Response: {response.text}"
            )


async def get_or_create_tag(tag: str, http_client: httpx.AsyncClient) -> int:
    """
    Retrieves a tag ID based on the tag name. Creates the tag if it doesn't exist.
    """
    logger.info(f"Processing tag: '{tag}'")  # Log the tag being processed
    if not tag:
        logger.error("Attempted to process an empty tag.")
        return None
    # Construct URLs for creating and retrieving tags
    tag_url = settings.T_LY_TAG_URL
    headers = {
        "Authorization": f"Bearer {settings.T_LY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Attempt to create the tag
    create_tag_response = await http_client.post(
        tag_url, json={"tag": tag}, headers=headers
    )

    # Check if the tag was successfully created or if it already exists
    if create_tag_response.status_code in [
        200,
        409,
    ]:  # Assuming 409 might indicate the tag already exists
        # Attempt to parse the JSON response to extract the tag ID
        try:
            tag_data = create_tag_response.json()
            tag_id = tag_data["id"]
            return tag_id
        except (KeyError, ValueError) as e:
            # Log the error and the response for debugging
            logger.error(
                f"Error parsing tag creation response: {e}. Response: {create_tag_response.text}"
            )
            raise
    else:
        # Log unsuccessful response for debugging
        logger.error(
            f"Failed to create or retrieve tag '{tag}'. Response: {create_tag_response.status_code}, {create_tag_response.text}"
        )
        raise Exception("Failed to create or retrieve tag.")


# Update: Using get_tags_ids function to manage tag creation and retrieval
async def get_tags_ids(tags: list[str], http_client: httpx.AsyncClient) -> list[int]:
    valid_tags = [tag for tag in tags if tag]  # Filter out empty strings
    tag_ids = []
    for tag in valid_tags:
        tag_id = await get_or_create_tag(tag, http_client)
        if tag_id:  # Ensure tag_id is not None or empty
            tag_ids.append(tag_id)
    return tag_ids
