# crud.py


from sqlalchemy import func, text, update
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

'''
Retry up to 3 times with a fixed wait of 1 second between attempts if an OperationalError is encountered.
'''
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def create_or_update_product(
    db: AsyncSession, product_data: dict, source_name: str
) -> Product:
    # Ensure source_id is set
    if not product_data["source_id"]:
        source_id = await get_source_id_by_name(db, source_name)
        product_data["source_id"] = source_id

    product_link = product_data.get("product_link")
    if product_link:
        # Query for an existing product
        existing_product_query = await db.execute(
            select(Product).filter_by(product_link=product_link)
        )
        existing_product = existing_product_query.scalars().first()

        if existing_product:
            # Initialize a flag to track if any updates are needed
            update_needed = False

            # Check for price or discount changes
            price_or_discount_changed = (
                existing_product.discount_percentage
                != product_data.get("discount_percentage")
                or existing_product.original_price != product_data.get("original_price")
                or existing_product.sale_price != product_data.get("sale_price")
            )

            # Check if image_url changed
            image_url_changed = existing_product.image_url != product_data.get(
                "image_url"
            )

            # Update product fields if changes are detected
            if price_or_discount_changed or image_url_changed:
                update_needed = True
                existing_product.discount_percentage = product_data.get(
                    "discount_percentage"
                )
                existing_product.original_price = product_data.get("original_price")
                existing_product.sale_price = product_data.get("sale_price")
                if image_url_changed:
                    existing_product.image_url = product_data.get("image_url")

            # Only create price history record if price changed
            if price_or_discount_changed:
                price_history_record = PriceHistory(
                    product_id=existing_product.id,
                    discount_percentage=product_data.get("discount_percentage"),
                    original_price=product_data.get("original_price"),
                    sale_price=product_data.get("sale_price"),
                )
                db.add(price_history_record)

            if update_needed:
                await db.commit()
                logger.info(f"Updated existing product: {product_link}")
            return existing_product

    # If the product does not exist, create a new one and its initial price history record
    new_product = Product(**product_data)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    price_history_record = PriceHistory(
        product_id=new_product.id,
        discount_percentage=product_data.get("discount_percentage"),
        original_price=product_data.get("original_price"),
        sale_price=product_data.get("sale_price"),
    )
    db.add(price_history_record)
    await db.commit()

    logger.info(f"Created new product and recorded its price: {product_link}")
    return new_product


async def get_unpublished_products(db: AsyncSession, country_lang: str):
    """
    Queries the database for a specific number of unpublished products for a given locale,
    ensuring a variety of brands using a complex SQL query.
    """
    sql_query = text(
        """
    WITH unique_brands AS (
        SELECT DISTINCT ON (brand) id
        FROM products
        WHERE published_at IS NULL
          AND country_lang = :country_lang
          AND discount_percentage >= :discount_threshold
        ORDER BY brand, RANDOM()
        LIMIT :limit
    ), additional_products AS (
        SELECT p.id
        FROM products p
        WHERE NOT EXISTS (SELECT 1 FROM unique_brands ub WHERE ub.id = p.id)
          AND published_at IS NULL
          AND country_lang = :country_lang
          AND discount_percentage >= :discount_threshold
        ORDER BY RANDOM()
        LIMIT (:limit - (SELECT COUNT(*) FROM unique_brands))
    )
    SELECT * FROM products
    WHERE id IN (SELECT id FROM unique_brands UNION ALL SELECT id FROM additional_products);
    """
    )

    # Executing the complex SQL query
    result = await db.execute(
        sql_query,
        {
            "country_lang": country_lang,
            "discount_threshold": settings.DISCOUNT_THRESHOLD,
            "limit": settings.PRODUCTS_TO_PUBLISH,
        },
    )
    # Directly map the SQL results to Product instances
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
    async with db.begin():
        # Check if the product is already marked as unavailable
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalars().first()

        if product and not product.available:
            # The product is already marked as unavailable, no need to update
            return

        # Mark the product as unavailable
        update_stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(
                available=False,
                unavailable_since=func.now()
                if not product.unavailable_since
                else product.unavailable_since,
            )
        )
        await db.execute(update_stmt)
        await db.commit()
