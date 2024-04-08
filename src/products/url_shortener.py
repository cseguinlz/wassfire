# src/utils.py or create a new src/url_shortener.py


import httpx

from src.config import settings  # Import your settings


async def shorten_url_with_tly(long_url: str, description: str, tags: list[str]) -> str:
    api_key = settings.T_LY_API_KEY
    request_url = settings.T_LY_LINK_URL
    tags_ids = await get_tags_ids(tags)  # Ensure all tags exist and get their IDs

    payload = {
        "long_url": long_url,
        "domain": settings.T_LY_DOMAIN,
        "description": description,
        "tags": tags_ids,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(request_url, json=payload, headers=headers)
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
    # Try to get the tag by name
    get_tag_response = await http_client.get(settings.T_LY_TAG_URL, params={"tag": tag})
    if get_tag_response.status_code == 200:
        # Tag exists, return its ID
        return get_tag_response.json()["id"]
    elif get_tag_response.status_code == 404:
        # Tag does not exist, create it
        create_tag_response = await http_client.post(
            settings.T_LY_TAG_URL, json={"tag": tag}
        )
        if create_tag_response.status_code == 200:
            # Tag created, return its ID
            return create_tag_response.json()["id"]
        else:
            raise Exception(
                f"Failed to create tag. Response: {create_tag_response.text}"
            )
    else:
        raise Exception(f"Failed to get tag. Response: {get_tag_response.text}")


async def get_tags_ids(tags: list[str]) -> list[int]:
    """
    Ensures all tags exist and returns their IDs.
    """
    async with httpx.AsyncClient() as client:
        tag_ids = [await get_or_create_tag(tag, client) for tag in tags]
    return tag_ids
