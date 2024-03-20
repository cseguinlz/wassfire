# src.whatsapp.service.py
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.products.service import queue_product_as_published
from src.utils import format_discount_percentage, format_euro_currency, setup_logger

logger = setup_logger(__name__)


async def publish_product_to_whatsapp(product, db: AsyncSession):
    logger.info(f"Publishing product {product.id}...")
    url = f"{settings.WHAPI_BASE_URL}/messages/image"
    payload = {
        "to": determine_channel(product),
        "caption": format_message(product),
        "media": product.image_url,
        "mime_type": "image/jpeg",
        "width": 500,
        "height": 500,
        # "ephemeral": 172800 TODO: Use for adds. Time in seconds for the message to be deleted, Max 604.800 = 7 días
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {settings.WHAPI_BEARER}",
    }
    try:
        async with httpx.AsyncClient(timeout=settings.WHAPI_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                logger.info(f"Product {product.id} published successfully.")
                # Prepare the product as published without committing yet
                await queue_product_as_published(db, product.id)
            else:
                logger.error(f"Failed to publish product {product.id}: {response.text}")
    except httpx.HTTPError as http_error:
        logger.error(f"HTTP request failed for product {product.id}: {http_error}")


def determine_channel(product):
    # TODO: channel mapping logic
    return settings.TEST_CHANNEL_ES


def format_message(product):
    # Create a message format that suits your needs
    return (
        f"🔥 *{format_discount_percentage(product.discount_percentage)}* descuento! - {product.brand}\n"
        f"🎁 {product.name}\n"
        f"💰 Eran {format_euro_currency(product.original_price)}. ¡Ahora a {format_euro_currency(product.sale_price)}!\n"
        f"👉🏼 Cómpralo directamente en {product.brand}:"
        f"{product.short_url}"
    )
