# src/products/publisher.py
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.products.service import get_unpublished_products
from src.products.url_shortener import shorten_url_with_tly
from src.utils import calculate_publish_delay, setup_logger
from src.whatsapp.service import publish_product_to_whatsapp

logger = setup_logger(__name__)


async def process_unpublished_products(db: AsyncSession):
    unpublished_products = await get_unpublished_products(db)
    if not unpublished_products:
        logger.info("No unpublished products found.")
        return

    product_count = len(unpublished_products)
    delay_seconds = calculate_publish_delay(product_count, settings.WHAPI_TIMEOUT)
    for product in unpublished_products:
        try:
            if product.discount_percentage >= settings.DISCOUNT_THRESHOLD:
                product.short_url = await shorten_url_with_tly(
                    product.product_link,
                    product.description,
                    [
                        product.brand,
                        product.category,
                        product.country_lang,
                        product.section,
                    ],
                )
                await publish_product_to_whatsapp(product, db)
                await asyncio.sleep(delay_seconds)
        except Exception as e:
            logger.error(f"Failed to publish product {product.id}: {e}", exc_info=True)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit product publications: {e}")
        raise
