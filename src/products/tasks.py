from src.database import get_db
from src.products.publisher import process_kids_products, process_unpublished_products
from src.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)


async def publish_products_task():
    logger.info("Publishing task started...")
    async for db in get_db():
        try:
            processed_count = await process_unpublished_products(db)
            logger.info(f"Processed count: {processed_count}")  # Log progress
            if processed_count > 0:
                await db.commit()  # Commit changes after successfully processing
            else:
                logger.info("No unpublished products found at this time.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during publication task: {e}", exc_info=True)
    logger.info("Publishing task completed.")


"""
Publish kids collection Portugal
"""


async def publish_kids_products_task():
    logger.info("Publishing Kids Products task started...")
    async for db in get_db():
        try:
            processed_count = await process_kids_products(
                db, "PT"
            )  # Instead of pt-PT so we include also en-PT, pt-PT
            logger.info(f"Processed count of kids products: {processed_count}")
            if processed_count > 0:
                await db.commit()
            else:
                logger.info("No kids products to publish at this time.")
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Error during kids products publication task: {e}", exc_info=True
            )
    logger.info("Publishing Kids Products task completed.")
