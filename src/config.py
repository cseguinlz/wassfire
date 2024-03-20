from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # DATABASE_URL: PostgresDsn = "postgresql+asyncpg://admin:AxN6hJoZk8BI@ep-purple-block-a2jfgchx.eu-central-1.aws.neon.tech/wassfiredb?sslmode=require"
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://admin:AxN6hJoZk8BI@ep-purple-block-a2jfgchx.eu-central-1.aws.neon.tech/wassfiredb"
    SITE_DOMAIN: str = "wassfire.com"
    TEST_CHANNEL_ES: str = "120363238296205954@newsletter"
    TEST_CHANNEL_LINK_ES: str = "https://whatsapp.com/channel/0029VaI8mEM65yDHPOfp362q"
    TEST_CHANNEL_PT: str = "120363213893060447@newsletter"
    WHAPI_BEARER: str = "k72Ap15pgweMuep5SjPjSDGF3Z2SXyDz"
    WHAPI_BASE_URL: str = "https://gate.whapi.cloud"
    WHAPI_TIMEOUT: int = 300  # Timeout in seconds
    DISCOUNT_THRESHOLD: float = 0.40
    T_LY_URL: str = "https://t.ly/api/v1/link/shorten"
    T_LY_API_KEY: str = "j2TkaKVMFpKj9GETDEYYSwKDo0rBf3STcZ6tXuO0HGmQOeHluD32L5ntKHdT"
    T_LY_DOMAIN: str = "https://wass.promo/"
    LEAD_SOURCE: str = "?source=wassfire.com"


settings = Config()
