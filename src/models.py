from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)

from src.database import Base

# TODO: Always check for new sections by diff brands/sources
""" class Section(enum.Enum):
    men = "Men"
    women = "Women"
    kids = "Kids"
    sports = "Sports"
    collections = "Collections" """


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    name = Column(String)
    country_lang = Column(String)
    brand = Column(String)
    section = Column(String)  # Column(Enum(Section)) TODO: when i18n ready
    category = Column(String)
    type = Column(String)
    color = Column(String)
    discount_percentage = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    sale_price = Column(Float, nullable=True)
    product_link = Column(String, unique=True)
    short_url = Column(String, nullable=True)
    source_published_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    image_url = Column(
        String
    )  # TODO: Needs to get image, upload to cheap storage (aws) and link it here
    second_image_url = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    country_lang = Column(String)
    source_link = Column(String)
    active = Column(Boolean, default=True)


class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
