from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
    ENVIRONMENT: Environment = (
        Environment.PRODUCTION
    )  # Default to production if not specified

    DATABASE_URL: PostgresDsn
    SITE_DOMAIN: str
    TEST_CHANNEL_ES: str
    TEST_CHANNEL_LINK_ES: str
    TEST_CHANNEL_PT: str
    WHAPI_BEARER: str
    WHAPI_BASE_URL: str
    WHAPI_TIMEOUT: int = 300  # Timeout in seconds
    DISCOUNT_THRESHOLD: float = 0.40
    T_LY_URL: str
    T_LY_API_KEY: str
    T_LY_DOMAIN: str
    LEAD_SOURCE: str
    SSL_CERT_PATH: str

    class Config:
        env_file = ".env"


settings = Config()
