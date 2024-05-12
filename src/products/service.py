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
    try:
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
    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of an error
        logger.error(f"SQLAlchemy Error in get_unpublished_products: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()  # Rollback in case of any other errors
        logger.error(f"Unexpected error in get_unpublished_products: {str(e)}")
        raise


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def get_unpublished_kids_products(db: AsyncSession, locale: str):
    sql_query = text(
        """
        WITH ranked_kids_products AS (
            SELECT id, brand,
                   ROW_NUMBER() OVER (PARTITION BY brand ORDER BY RANDOM()) as rank
            FROM products
            WHERE (section IN ('Kids', 'Niños', 'Crianças', 'CRIANÇA', 'NIÑOS') OR
                   category IN ('Kids', 'Niños', 'Crianças') OR
                   type IN ('Kids', 'Niños', 'Crianças'))
              AND discount_percentage >= :discount_threshold
              AND country_lang LIKE :country_lang
              AND published_at IS NULL
        )
        SELECT p.*
        FROM products p
        JOIN ranked_kids_products rkp ON p.id = rkp.id
        WHERE rkp.rank <= :limit;
        """
    )
    try:
        # Execute the query with parameters for locale and limits on the number of products per brand
        result = await db.execute(
            sql_query,
            {
                "country_lang": f"%{locale}%",  # Formats to %PT% so Like () works cause local=pt, so we include also pt-EU, pt-EN
                "discount_threshold": settings.DISCOUNT_THRESHOLD,
                "limit": settings.PRODUCTS_TO_PUBLISH,
            },
        )
        # Print compiled query for debugging
        compiled_query = sql_query.compile(compile_kwargs={"literal_binds": True})
        print(compiled_query)
        products = [Product(**row) for row in result.mappings().all()]
        logger.info(f"Fetched {len(products)} products")
        return products
    except SQLAlchemyError as e:
        await db.rollback()  # Rollback in case of an error
        logger.error(f"SQLAlchemy Error in get_unpublished_kids_products: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()  # Rollback in case of any other errors
        logger.error(f"Unexpected error in get_unpublished_kids_products: {str(e)}")
        raise


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
    update_query = text(
        """
    UPDATE products 
    SET available = False, unavailable_since = COALESCE(unavailable_since, NOW()) 
    WHERE id = :id AND available = True
    """
    )  # Only update if currently available to avoid unnecessary writes

    try:
        if not db.in_transaction():
            async with db.begin():
                await db.execute(update_query, {"id": product_id})
        else:
            await db.execute(update_query, {"id": product_id})
    except Exception as e:
        if db.in_transaction():
            await db.rollback()
        logger.error(f"Error marking product {product_id} as unavailable: {e}")
        raise


async def update_existing_product(
    db: AsyncSession, existing_product: Product, product_data: dict
) -> bool:
    # Initialize a flag to track if any updates are needed
    update_needed = False

    # Check for any changes in the relevant fields
    fields_to_check = [
        "discount_percentage",
        "original_price",
        "sale_price",
        "image_url",
        "section",
        "type",
    ]

    # Determine if any field has changed
    for field in fields_to_check:
        if getattr(existing_product, field) != product_data.get(field):
            setattr(existing_product, field, product_data.get(field))
            update_needed = True

    # If there's a price or discount change, add a new price history record
    if any(
        getattr(existing_product, field) != product_data.get(field)
        for field in ["discount_percentage", "original_price", "sale_price"]
    ):
        price_history_record = PriceHistory(
            product_id=existing_product.id,
            discount_percentage=product_data.get("discount_percentage"),
            original_price=product_data.get("original_price"),
            sale_price=product_data.get("sale_price"),
        )
        db.add(price_history_record)

    return update_needed
