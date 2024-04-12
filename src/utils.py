import json
import logging
import sys
from datetime import datetime, timezone

from fastapi import Request

from src.config import settings


def setup_logger(name, level=None):
    """
    Set up and return a logger with the given name and level.
    """
    # Determine the logging level
    if level is None:
        level = settings.LOG_LEVEL  ## log level per environment

    # Convert level from string to logging constant if necessary
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger


# Initialize logger
logger = setup_logger(__name__)


def get_user_locale(request: Request) -> str:
    # Get the first locale from the Accept-Language header
    locale = request.headers.get("Accept-Language", "en").split(",")[0]
    # Split off any quality value and take only the locale part
    locale = locale.split(";")[0]
    return locale


def load_translations(locale: str = None, directory: str = "src/locales"):
    if not locale:
        # Default to English if not set
        locale = "en"
    try:
        with open(f"{directory}/{locale}.json", "r") as file:
            translations = json.load(file)
    except FileNotFoundError:
        with open(f"{directory}/en.json", "r") as file:
            translations = json.load(file)
    return translations


async def get_translations(request: Request) -> dict:
    locale = get_user_locale(request)
    translations = load_translations(locale)
    return translations


def format_currency(value: float, locale: str = "es-ES") -> str:
    """
    Manually format a float value as a currency string, adjusting for locale.
    Render doesn't provide custom locales.
        Render Native Runtimes have a very limited set of locales to keep image sizes down, e.g.:
        ~/project/src$ locale -a
        C
        C.UTF-8
        POSIX

        If you need a custom locale you would need to create your own environment with Docker.>

    :param value: The float value to format.
    :param locale: The locale code, which determines the formatting.
    :return: A string representing the value as a currency.
    """
    # Define locale-based formatting rules
    if locale.lower().startswith("en"):
        # English formatting: 1,234,567.89 €
        formatted_value = f"{value:,.2f} €"
    else:
        # European formatting: 1.234.567,89 €
        # Format the number manually with thousands as '.' and decimal as ','
        formatted_value = (
            f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        formatted_value += " €"

    return formatted_value


async def convert_price_to_float(price_str):
    try:
        return float(price_str.replace("€", "").replace(",", ".").strip())
    except ValueError:
        return None


def get_utc_time():
    return datetime.now(timezone.utc)


def format_discount_percentage(discount: float) -> str:
    """
    Formats a discount given as a float (e.g., 0.55 for 55% discount)
    into a string with a percent sign (e.g., "55%").
    """
    # Convert to percentage, round to nearest integer, and format as a string with a percent sign
    return f"{discount * 100:.0f}%"
