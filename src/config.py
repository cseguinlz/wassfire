from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    ENVIRONMENT: Environment = (
        Environment.PRODUCTION
    )  # Default to production if not specified

    DATABASE_URL: PostgresDsn
    DATABASE_URL_PRE: PostgresDsn
    SITE_DOMAIN: str
    TEST_CHANNEL_ES: str
    TEST_CHANNEL_PT: str
    WHATSAPP_CHANNEL_ES: str
    WHATSAPP_CHANNEL_PT: str
    WHAPI_BEARER: str
    WHAPI_BASE_URL: str
    WHAPI_TIMEOUT: int = 300  # Timeout in seconds
    DISCOUNT_THRESHOLD: float
    T_LY_LINK_URL: str
    T_LY_TAG_URL: str
    T_LY_API_KEY: str
    T_LY_DOMAIN: str
    LEAD_SOURCE: str
    SSL_CERT_PATH: str
    PUBLISH_HOURS: str
    SUPPORTED_LOCALES: str
    PRODUCTS_TO_PUBLISH: int
    LOG_LEVEL: str

    class Config:
        env_file = ".env"


settings = Config()
