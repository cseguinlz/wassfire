import json
import locale
import logging
import sys
from datetime import datetime, timezone

from fastapi import Request


def setup_logger(name):
    """
    Set up and return a logger with the given name.
    """
    # Configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # or DEBUG, ERROR, etc.

    # Create console handler and set level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)  # or DEBUG, ERROR, etc.

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
    logger.debug(f"Translations: {translations}")
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
        formatted_value = locale.currency(value, grouping=True)
        # Restore the original locale
        locale.setlocale(locale.LC_ALL, current_locale)
        return formatted_value
    except (locale.Error, ValueError) as e:
        logger.debug(f"Error formatting currency: {e}")
        return str(value)


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
