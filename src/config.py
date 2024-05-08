from pydantic import EmailStr, PostgresDsn
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
    SSL_CERT_PATH: str
    PUBLISH_HOURS: str
    READING_SOURCES_DAY: str
    READING_SOURCES_HOUR_RANGE: str
    SUPPORTED_LOCALES: str
    PRODUCTS_TO_PUBLISH: int
    LOG_LEVEL: str
    # Email configurations (Add these)
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    MAIL_USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    class Config:
        env_file = ".env"


settings = Config()
