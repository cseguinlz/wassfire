# src/utils.py or create a new src/url_shortener.py


import httpx

from src.config import settings  # Import your settings


async def shorten_url_with_tly(long_url: str, description: str, tags: list[str]) -> str:
    api_key = settings.T_LY_API_KEY
    request_url = settings.T_LY_URL
    payload = {
        "long_url": long_url,
        "domain": settings.T_LY_DOMAIN,
        "description": description,
        "tags": tags,
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
