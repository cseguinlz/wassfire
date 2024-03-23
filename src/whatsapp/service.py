# src.whatsapp.service.py

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.products.service import queue_product_as_published
from src.utils import (
    format_discount_percentage,
    format_euro_currency,
    load_translations,
    setup_logger,
)

logger = setup_logger(__name__)


async def publish_product_to_whatsapp(product, db: AsyncSession):
    logger.info(f"Publishing product {product.id}...")
    url = f"{settings.WHAPI_BASE_URL}/messages/image"

    # Extract locale from the product's country_lang field
    locale = product.country_lang.split("_")[0]
    translations = load_translations(locale)

    payload = {
        "to": determine_channel(locale),
        "caption": format_message(product, translations),
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


def determine_channel(locale):
    # Assuming there's a way to check if it's a test environment
    is_test = settings.ENVIRONMENT.is_debug

    # Mapping logic based on locale
    if locale == "es":
        return settings.TEST_CHANNEL_ES if is_test else settings.WHATSAPP_CHANNEL_ES
    elif locale == "pt":
        return settings.TEST_CHANNEL_PT if is_test else settings.WHATSAPP_CHANNEL_PT

    # Default channel or error handling if locale is not recognized
    return (
        settings.TEST_CHANNEL_ES if is_test else settings.WHATSAPP_CHANNEL_ES
    )  # or any other default action


def format_message(product, translations):
    # Format dynamic parts of the message
    discount_percentage = format_discount_percentage(product.discount_percentage)
    original_price = format_euro_currency(product.original_price)
    sale_price = format_euro_currency(product.sale_price)

    # Use the loaded translations to construct the message
    message = translations["whatsapp_message"].format(
        discount_percentage=discount_percentage,
        brand=product.brand,
        name=product.name,
        original_price=original_price,
        sale_price=sale_price,
        short_url=product.short_url,
    )

    return message
