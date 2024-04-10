import httpx


async def is_product_available(product_url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(product_url, follow_redirects=True)
            return response.status_code == 200
    except httpx.RequestError:
        return False
