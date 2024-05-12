import ssl
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

# Uncomment to test
is_pre = settings.ENVIRONMENT.is_debug
DATABASE_URL = str(settings.DATABASE_URL_PRE) if is_pre else str(settings.DATABASE_URL)

# Used only to read from sources from local, 403s in Pro for Adidas and Carhartt
# DATABASE_URL = str(settings.DATABASE_URL)


# Create an SSL context with path depending on environment
ssl_context = ssl.create_default_context(cafile=settings.SSL_CERT_PATH)
ssl_context.check_hostname = True  # Enable hostname verification
ssl_context.verify_mode = ssl.CERT_REQUIRED  # Ensure the certificate is required

# Create the async engine with the SSL context
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # change to True for intensive logging!
    connect_args={"ssl": ssl_context},
    pool_size=20,
    max_overflow=10,
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
        # Begin a transaction by default at the start of the block
        await async_session.begin()
        yield async_session
        # Commit the transaction at the end of the block if no errors occurred
        await async_session.commit()
    except Exception as e:
        # Rollback the transaction in case of an error
        await async_session.rollback()
        raise e
    finally:
        # Close the session whether or not there were errors
        await async_session.close()


db_depency = Annotated[Session, Depends(get_db)]
