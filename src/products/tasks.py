from src.database import get_db
from src.products.publisher import process_unpublished_products
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
