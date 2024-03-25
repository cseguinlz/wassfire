import json
import locale
import logging
import random
import sys
from datetime import datetime, timezone

from fastapi import Request


def get_user_locale(request: Request) -> str:
    locale = request.headers.get("Accept-Language", "en").split(",")[0]
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
        formatted_value = locale.currency(value, grouping=True)
        # Restore the original locale
        locale.setlocale(locale.LC_ALL, current_locale)
        return formatted_value
    except (locale.Error, ValueError) as e:
        print(f"Error formatting currency: {e}")
        return str(value)


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


async def convert_price_to_float(price_str):
    try:
        return float(price_str.replace("€", "").replace(",", ".").strip())
    except ValueError:
        return None


def get_utc_time():
    return datetime.now(timezone.utc)


def calculate_publish_delay(product_count: int, total_time_seconds: int) -> float:
    """
    Calculate a random delay within a specified range between publishing each product to ensure
    all products are published within the specified total time while adhering to the min and max delay limits.

    :param product_count: The total number of products to publish.
    :param total_time_seconds: The total time in seconds within which all products should be published.
    :return: The delay in seconds between publishing each product.
    """
    if product_count > 1:
        # Calculate the maximum delay as the total time divided by the number of intervals
        max_delay = total_time_seconds / max(1, product_count - 1)
        min_delay = 2
    # Generate a random delay within the min and dynamically calculated max range
    return random.uniform(min_delay, max_delay)


def format_discount_percentage(discount: float) -> str:
    """
    Formats a discount given as a float (e.g., 0.55 for 55% discount)
    into a string with a percent sign (e.g., "55%").
    """
    # Convert to percentage, round to nearest integer, and format as a string with a percent sign
    return f"{discount * 100:.0f}%"
