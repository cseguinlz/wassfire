# README - WassFire Project Overview
 Wassfire is an Instant Messaging-commerce platform. 
 
 It syndicates highly discounted products from top brands e-commerce sites and publish them on WhatsApp channels. Those published products link directly to their original brand listing, so basically, Wasfire generates traffic for those deals

## Main Components

### Web Scraping

The web scraping component is structured as follows:

- **`websources/router.py`**:
  - **`read_adidas()`** function to initiate the scraping process.

#### Workflow:
1. **Fetching Pages**:
   - **`fetch_page()`**: Ensures the response from a webpage is correctly retrieved.
   - **`urls.py`**: Manually add URLs to scrape. Capture AJAX calls if the page loads on scroll and write the response to a file.

2. **Parsing Pages**:
   - **`parse_page()`**: Function to test with the saved response file.

3. **Scraping Functions**:
   - **`scrape_<brand>()`**: Specific functions for each brand.
   - **`scrape_and_save_products()`**: General function to scrape and save products.

4. **Source Creation via API**:
   - **`/create_source`**: Endpoint to manually set the source's name, ID, etc.

### Database Schema Modifications

Steps to modify the database schema include:

1. **Modify Models**:
   - Update or add columns in `models.py`.

2. **Update Schemas**:
   - Reflect changes in `schemas.py`.

3. **Alembic Revisions**:
   - Generate new Alembic revision scripts: `alembic revision --autogenerate -m "describe changes here"`.

4. **Review & Modify Scripts**:
   - Manually review and potentially modify scripts in `alembic/versions`.

5. **Upgrade Database Schema**:
   - Apply changes with: `alembic upgrade head`.

### Publishing Products to WhatsApp

Workflow for publishing products to WhatsApp channels:

- **`main.py`**:
  - **`setup_scheduler(app)`**: Sets up scheduled tasks.
- **`scheduler.py`**:
  - Calls `tasks.py` for task execution.
- **`tasks.py`**:
  - **`publish_products_task()`**: Scheduled task for product publication.
- **`publisher.py`**:
  - **`process_unpublished_products(db: AsyncSession)`**: Processes products that need publishing.
- **`whatsapp/service.py`**:
  - **`publish_product_to_whatsapp(product, db: AsyncSession)`**: Function to publish a product to WhatsApp.

### Internationalization (i18n)

Process for handling internationalization:

- **`src/home/routers.py`**:
  - Calls utility functions to determine user's locale and load corresponding translations.
- **`src/utils.py`**:
  - **`get_translations()`**: Retrieves translation data based on user's locale.
- Translation files located in:
  - **`src/locales/{locale}.json`**.

### Logging

Setup and usage of logging throughout the application:

- **Setup**: 
  - Create a logger by specifying the name and level (info, debug, warning, error) in `src/utils.py`.
  - **`setup_logger(name, level=None)`**: Configures the logging level which can be set via an environment variable in `.env` and `src/config.py` as `LOG_LEVEL=DEBUG`.

#### Example Usage:
```python
from src.utils import setup_logger

# Initialize logger
logger = setup_logger(__name__)

async def read_sources_task():
    logger.debug("Reading sources task started...")
