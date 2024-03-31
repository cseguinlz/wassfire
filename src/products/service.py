# crud.py

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    if not product_data["source_id"]:
        source_id = await get_source_id_by_name(db, source_name)
        product_data["source_id"] = source_id
    product_link = product_data.get("product_link")
    if product_link:
        existing_product_query = await db.execute(
            select(Product).filter_by(product_link=product_link)
        )
        existing_product = existing_product_query.scalars().first()

        if existing_product:
            # Record a price change if there's a difference
            price_or_discount_changed = (
                existing_product.discount_percentage
                != product_data.get("discount_percentage")
                or existing_product.original_price != product_data.get("original_price")
                or existing_product.sale_price != product_data.get("sale_price")
            )
            if price_or_discount_changed:
                price_history_record = PriceHistory(
                    product_id=existing_product.id,
                    discount_percentage=product_data.get("discount_percentage"),
                    original_price=product_data.get("original_price"),
                    sale_price=product_data.get("sale_price"),
                )
                db.add(price_history_record)
                print(f"Recorded price change for product: {product_link}")

            # Update the product with the new details
            existing_product.discount_percentage = product_data.get(
                "discount_percentage"
            )
            existing_product.original_price = product_data.get("original_price")
            existing_product.sale_price = product_data.get("sale_price")

            await db.commit()
            print(f"Updated existing product: {product_link}")
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

    print(f"Created new product and recorded its price: {product_link}")
    return new_product


async def get_unpublished_products(db: AsyncSession):
    """
    Queries the database for products that have not been published yet
    """
    query = select(Product).filter(Product.published_at.is_(None))
    result = await db.execute(query)
    products = result.scalars().all()
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
        print(f"Database update failed: {e}")
