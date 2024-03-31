# pydantic models

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel


def convert_datetime_to_gmt(dt: datetime) -> str:
    """Converts a datetime object to the ISO 8601 format in UTC."""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CustomBaseModel(BaseModel):
    class Config:
        json_encoders = {datetime: convert_datetime_to_gmt}
        from_attributes = True


class SourceBase(CustomBaseModel):
    name: str
    country_lang: Optional[str] = None
    source_link: Optional[str] = None
    active: Optional[bool] = True


class SubscriberBase(CustomBaseModel):
    email: str


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int

    class Config:
        from_attributes = True


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberResponse(SubscriberBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(CustomBaseModel):
    name: str
    description: str
    country_lang: str
    brand: str
    section: str
    category: str
    type: str
    color: str
    discount_percentage: float
    original_price: float
    sale_price: float
    product_link: str
    short_url: str
    source_published_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    image_url: str
    second_image_url: str


class PriceHistoryBase(CustomBaseModel):
    discount_percentage: Optional[float] = None
    original_price: float
    sale_price: float
    recorded_at: datetime


class PriceHistoryResponse(PriceHistoryBase):
    id: int


class ProductCreate(ProductBase):
    source_id: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    source_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    price_history: List[
        PriceHistoryResponse
    ] = []  # Assuming you want to include price history in your product responses

    class Config:
        from_attributes = True
