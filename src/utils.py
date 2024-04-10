import json
import locale
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


def format_euro_currency(value: float, locale_str: str = "es_ES.UTF-8") -> str:
    """
    Format a float value as a currency string in euros, based on the specified locale.

    :param value: The float value to format.
    :param locale_str: The locale to use for formatting.
    :return: A string representing the value as a currency in euros.
    """
    try:
        # Save the current locale
        current_locale = locale.getlocale()
        # Set the desired locale for currency formatting
        locale.setlocale(locale.LC_ALL, locale_str)
        # Use locale.currency to format the number, then replace the currency symbol with € manually
        formatted_value = locale.currency(value, symbol=False, grouping=True) + " €"
        # Restore the original locale
        locale.setlocale(locale.LC_ALL, current_locale)
        return formatted_value
    except (locale.Error, ValueError) as e:
        logger.debug(f"Error formatting currency: {e}")
        return f"{value} €"  # Fallback to a simple format


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
