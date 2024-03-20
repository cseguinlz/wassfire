from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.products import service
from src.schemas import (
    ProductCreate,
    ProductResponse,
    SourceCreate,
    SourceResponse,
)

router = APIRouter()


# Create a Source
@router.post("/sources/", response_model=SourceResponse)
async def create_source(source: SourceCreate, db: AsyncSession = Depends(get_db)):
    db_source = await service.create_source(db=db, source_data=source.model_dump())
    return db_source


# Get a single Source
@router.get("/sources/{source_id}", response_model=SourceResponse)
async def read_source(source_id: int, db: AsyncSession = Depends(get_db)):
    db_source = await service.get_source(db=db, source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source


# Create a Product linked to a Source
@router.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    # Ensure the source exists
    db_source = await service.get_source(db=db, source_id=product.source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    db_product = await service.create_product(db=db, product_data=product.model_dump())
    return db_product


# Get a single Product
@router.get("/products/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await service.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


# Get Products by Source
@router.get("/products/source/{source_id}", response_model=List[ProductResponse])
async def read_products_by_source(source_id: int, db: AsyncSession = Depends(get_db)):
    products = await service.get_products_by_source(db=db, source_id=source_id)
    return products
