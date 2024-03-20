import pytest
from aioresponses import aioresponses

from src.web_sources.adidas.adidas_html_old import parse_page, scrape_adidas

@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m

@pytest.mark.asyncio
async def test_parse_page():
    # Sample HTML content simulating a part of the adidas outlet page
    # Read the HTML content from the file
    with open('adidas_es.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Expected output based on the mock HTML content
    expected_output = [
        {
            "name": "Product Name",
            "category": "Product Category",
            # Add more keys as needed based on your parse_page function
        }
    ]
    # Call the parse_page function with the mock HTML and compare the result
    assert await parse_page(html_content) == expected_output


@pytest.mark.asyncio
async def test_scrape_adidas(mock_aioresponse):
    # Mocking the HTTP request made within the scrape_adidas function
    mock_url = "https://www.adidas.es/calzado-hombre-outlet"
    mock_aioresponse.get(mock_url, status=200, body="<html>Mocked HTML response</html>")

    # Assuming scrape_adidas is modified to return data for testing
    # You might need to adjust this part based on the actual implementation
    data = await scrape_adidas()
    assert data is not None  # Or more specific assertions based on your return values
