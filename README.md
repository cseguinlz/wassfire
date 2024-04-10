## Main components:
### Retrieving data from a Web Source (web scrapping)

`websources/router.py` --> `read_adidas()` --> `scrape`

- 1: Create fetch_page to make sure we understand what's on the response
  - create urls.py and add manually urls to scrape
  - If load on scroll capture AJAX call.
  - Write to a file response
- 2: Create parse_page() function
  - Test with response file
- 3: Implement functions:
  - scrape_<brand>()
  - scrape_and_save_products()
- 4: Create Source through api /create_source
  - Set name, id etc manually


### Modifying the DB schema
- 1: Add/remove column to object in `models.py`
- 2: Update `schemas.py`
- 3: Generate alembic revison scripts to update DB schema:
`alembic revision --autogenerate -m "some comment"`
- 4: Review update script in `alembic/versions` and modify if needed
- 5: Update DB schema: `alembic upgrade head`

### Publish products to Whatsapp task:
`main.py --> setup_scheduler(app)` --> `scheduler.py --> setup_scheduler(app)` --> `tasks.py --> publish_products_task()` --> `publisher.py --> process_unpublished_products(db: AsyncSession)` --> `whatsapp/service.py --> publish_product_to_whatsapp(product, db: AsyncSession)`

### i18n
`src/home/routers.py` --> `src/utils.py --> get_translations() --> get_user_locale(request) --> load_translations(locale)` ---> `src/locales/{locales}.json`


### Logs
Create logger indicating name and level (info, debug, warning, error).
`src/utils.py`--> `setup_logger(name, level=None)`

Level is set by an environmental variable at `.env` and `src/config.py settings` as `LOG_LEVEL=DEBUG`

# Usage:
```from src.utils import setup_logger
  # Initialize logger
logger = setup_logger(__name__)

async def read_sources_task():
    logger.debug("Reading sources task started...")```