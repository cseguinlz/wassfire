import asyncio

from bs4 import BeautifulSoup

from src.web_sources.utils import fetch_page  # Adjust the import path as necessary


async def validate_html_structure(html_content: str) -> bool:
    soup = BeautifulSoup(html_content, "html.parser")

    # Define the selectors based on your scraping function
    selectors = [
        ".glass-product-card",
        '[data-auto-id="product-card-title"]',
        '[data-auto-id="product-card-category"]',
        '[data-auto-id="product-card-colvar-count"]',
        '[data-auto-id="glass-hockeycard-link"]',
        ".glass-product-card__assets-link img",
        ".discount-badge___318Q7",
        ".gl-price-item",
    ]

    # Check each selector for presence in the HTML
    for selector in selectors:
        if not soup.select(selector):
            print(f"Missing or changed HTML structure for selector: {selector}")
            return False

    print("HTML structure is valid based on defined selectors.")
    return True


async def check_page_structure(url: str):
    html_content = await fetch_page(
        url
    )  # Assuming this returns HTML content directly as a string
    if html_content:  # No need to check status_code or call .text() method
        return validate_html_structure(html_content)
    else:
        print("Failed to fetch HTML content or page returned empty response.")
        return False


# Example usage
async def main():
    url = "https://www.adidas.es/calzado-hombre-outlet"
    if not await check_page_structure(url):
        print("🚨 HTML structure changed or page is unavailable! 🚨")
        # TODO: Implement alerting/notification
    else:
        print("✅ Page structure is consistent with expectations. ✅")


if __name__ == "__main__":
    asyncio.run(main())
