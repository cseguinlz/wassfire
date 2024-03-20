from typing import Annotated
import ssl
from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_URL)

# Create an SSL context
ssl_context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
ssl_context.check_hostname = True  # Enable hostname verification
ssl_context.verify_mode = ssl.CERT_REQUIRED  # Ensure the certificate is required

# Create the async engine with the SSL context
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": ssl_context}
)


# Create a sessionmaker instance with AsyncSession
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


async def get_db():
    async_session = AsyncSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()


db_depency = Annotated[Session, Depends(get_db)]
