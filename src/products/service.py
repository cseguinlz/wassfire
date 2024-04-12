# crud.py


from sqlalchemy import text, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from tenacity import retry, stop_after_attempt, wait_fixed

from src.config import settings
from src.models import PriceHistory, Product, Source
from src.utils import get_utc_time, setup_logger

logger = setup_logger(__name__)


async def create_source(db: AsyncSession, source_data: dict) -> Source:
    new_source = Source(**source_data)
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source


async def get_source(db: AsyncSession, source_id: int) -> Source:
    query = select(Source).where(Source.id == source_id)
    result = await db.execute(query)
    source = result.scalars().first()
    return source


async def get_source_id_by_name(db: AsyncSession, source_name: str) -> int:
    result = await db.execute(select(Source.id).where(Source.name == source_name))
    source_id = result.scalars().first()
    if source_id:
        return source_id
    else:
        # Handle the case where the source is not found
        # For example, create a new source or raise an error
        raise ValueError(f"Source not found with name: {source_name}")


async def create_product(
    db: AsyncSession, product_data: dict, source_name: str
) -> Product:
    try:
        logger.debug(f"Attempting to save product: {product_data['name']}")
        if not product_data["source_id"]:
            source_id = await get_source_id_by_name(db, source_name)
            product_data["source_id"] = source_id
        new_product = Product(**product_data)
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        logger.debug(f"Product saved: {product_data['name']}")
        return new_product
    except Exception as e:
        logger.error(f"Failed to save product {product_data['name']}: {e}")
        raise


async def get_product(db: AsyncSession, product_id: int) -> Product:
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalars().first()
    return product


async def get_products_by_source(db: AsyncSession, source_id: int) -> list[Product]:
    query = select(Product).where(Product.source_id == source_id)
    result = await db.execute(query)
    products = result.scalars().all()
    return products


async def create_or_update_product(
    db: AsyncSession, product_data: dict, source_name: str
) -> Product:
    try:
        # Ensure source_id is set
        if not product_data["source_id"]:
            source_id = await get_source_id_by_name(db, source_name)
            product_data["source_id"] = source_id

        product_link = product_data.get("product_link")
        existing_product = None
        if product_link:
            # Query for an existing product
            existing_product_query = await db.execute(
                select(Product).filter_by(product_link=product_link)
            )
            existing_product = existing_product_query.scalars().first()

        if existing_product:
            # Function to update existing product
            update_needed = await update_existing_product(
                db, existing_product, product_data
            )

            # Only commit if updates are made to minimize unnecessary commits
            if update_needed:
                await db.commit()
                logger.info(f"Updated existing product: {product_link}")
        else:
            # If the product does not exist, create a new one
            new_product = Product(**product_data)
            db.add(new_product)
            await db.commit()  # Commit to ensure new_product gets an ID
            await db.refresh(new_product)  # Refresh to load the ID

            # Create initial price history record for new product
            price_history_record = PriceHistory(
                product_id=new_product.id,
                discount_percentage=product_data.get("discount_percentage"),
                original_price=product_data.get("original_price"),
                sale_price=product_data.get("sale_price"),
            )
            db.add(price_history_record)

            await db.commit()
            await db.refresh(new_product)
            logger.info(f"Created new product and recorded its price: {product_link}")

        return existing_product if existing_product else new_product

    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing product {product_link}: {e}")
        raise


"""
Retry up to 3 times with a fixed wait of 1 second between attempts if an OperationalError is encountered.
"""


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def get_unpublished_products(db: AsyncSession, locale: str):
    """
    Queries the database for unpublished products for a given locale,
    ensuring up to settings.PRODUCTS_TO_PUBLISH products are selected.
    """
    sql_query = text(
        """
        WITH ranked_products AS (
            SELECT id, brand,
                   ROW_NUMBER() OVER (PARTITION BY brand ORDER BY RANDOM()) as rank
            FROM products
            WHERE published_at IS NULL
              AND country_lang = :country_lang
              AND discount_percentage >= :discount_threshold
        )
        SELECT p.*
        FROM products p
        JOIN ranked_products rp ON p.id = rp.id
        WHERE rp.rank <= :limit;
        """
    )

    # Execute the query
    result = await db.execute(
        sql_query,
        {
            "country_lang": locale,
            "discount_threshold": settings.DISCOUNT_THRESHOLD,
            "limit": settings.PRODUCTS_TO_PUBLISH,
        },
    )
    products = [Product(**row) for row in result.mappings().all()]
    return products


async def queue_product_as_published(db: AsyncSession, product_id: int):
    # Use the product_id to find and update to ensure session awareness
    try:
        await db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(published_at=get_utc_time(), updated_at=get_utc_time())
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.debug(f"Database update failed: {e}")


async def mark_product_as_unavailable(product_id: int, db: AsyncSession):
    """
    Marks a product as unavailable in the database.

    Args:
        product_id (int): The ID of the product to mark as unavailable.
        db (AsyncSession): The database session.
    """
    try:
        update_query = text("UPDATE products SET available = False WHERE id = :id")

        if not db.in_transaction():
            # Start a new transaction if one isn't already in progress
            async with db.begin():
                await db.execute(update_query, {"id": product_id})
        else:
            # If already in a transaction, just execute the update
            await db.execute(update_query, {"id": product_id})

    except Exception as e:
        # Rollback in case of an exception if a transaction is ongoing
        if db.in_transaction():
            await db.rollback()
        logger.error(f"Error marking product {product_id} as unavailable: {e}")
        raise


async def update_existing_product(
    db: AsyncSession, existing_product: Product, product_data: dict
) -> bool:
    # Initialize a flag to track if any updates are needed
    update_needed = False

    # Check for price or discount changes
    price_or_discount_changed = (
        existing_product.discount_percentage != product_data.get("discount_percentage")
        or existing_product.original_price != product_data.get("original_price")
        or existing_product.sale_price != product_data.get("sale_price")
    )

    # Check if image_url changed
    image_url_changed = existing_product.image_url != product_data.get("image_url")

    # Update product fields if changes are detected
    if price_or_discount_changed or image_url_changed:
        update_needed = True
        existing_product.discount_percentage = product_data.get("discount_percentage")
        existing_product.original_price = product_data.get("original_price")
        existing_product.sale_price = product_data.get("sale_price")
        if image_url_changed:
            existing_product.image_url = product_data.get("image_url")

    # Only create a price history record if price changed
    if price_or_discount_changed:
        price_history_record = PriceHistory(
            product_id=existing_product.id,
            discount_percentage=product_data.get("discount_percentage"),
            original_price=product_data.get("original_price"),
            sale_price=product_data.get("sale_price"),
        )
        db.add(price_history_record)
        # No need for a separate commit here; it will be handled in the calling function

    return update_needed
