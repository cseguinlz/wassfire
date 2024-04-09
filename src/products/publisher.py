# src/products/publisher.py
import asyncio
import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.products.service import get_unpublished_products
from src.products.url_shortener import shorten_url_with_tly
from src.utils import setup_logger
from src.whatsapp.service import publish_product_to_whatsapp

logger = setup_logger(__name__)


async def process_unpublished_products(db: AsyncSession) -> int:
    total_published = 0
    for locale in settings.SUPPORTED_LOCALES.split(","):
        # Special handling for Portuguese locales to prevent duplication
        if (
            locale.startswith("pt")
            and "pt-PT" in settings.SUPPORTED_LOCALES.split(",")
            and locale != "pt-PT"
        ):
            continue

        unpublished_products = await get_unpublished_products(db, locale)

        if not unpublished_products:
            logger.info(f"No unpublished products found for {locale}.")
            continue  # Continue with the next locale if no products found

        for index, product in enumerate(unpublished_products):
            try:
                # Publish only products over 40% discount
                if product.discount_percentage >= settings.DISCOUNT_THRESHOLD:
                    is_dev = settings.ENVIRONMENT.is_debug
                    # Generate short url only for PRO
                    if is_dev:
                        product.short_url = "wass.promo/something"
                    else:
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
                # Only wait if this is not the last product
                if index < len(unpublished_products) - 1:
                    delay_seconds = random.randint(
                        45, 70
                    )  # Random delay between 45 and 70 seconds
                    await asyncio.sleep(delay_seconds)
            except Exception as e:
                logger.error(
                    f"Failed to publish product {product.id}: {e}", exc_info=True
                )
        total_published += len(unpublished_products)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit product publications: {e}")
        raise

    return total_published
