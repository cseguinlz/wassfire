from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.products.publisher import process_unpublished_products
from src.utils import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/publish-products")
async def publish_products(db: AsyncSession = Depends(get_db)):
    try:
        processed_count = await process_unpublished_products(db)
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit product publications: {e}")
        raise HTTPException(status_code=500, detail="Failed to commit product updates.")

    if processed_count == 0:
        raise HTTPException(status_code=404, detail="No unpublished products found")

    return {
        "message": "All unpublished products processed successfully.",
        "published_products_count": processed_count,
    }
