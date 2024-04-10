import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.products.tasks import publish_products_task
from src.utils import setup_logger
from src.web_sources.tasks import read_sources_task

scheduler = AsyncIOScheduler()

# Initialize logger
logger = setup_logger(__name__)


def setup_scheduler(app):
    logger.debug("Setting up scheduler...")
    # Schedule the task to run three times a day at 9 AM, 3 PM, and 9 PM
    scheduler.add_job(
        publish_products_task,
        trigger=CronTrigger(hour=settings.PUBLISH_HOURS),
        id="publish_products",  # Unique ID for the job
        replace_existing=True,
    )

    # New task: Scrape web sources once a week on Mon, Tue, or Wed at a random hour
    random_day_of_week = random.choice(["mon", "tue", "wed"])
    random_hour = random.randint(0, 23)  # Random hour of the day

    scheduler.add_job(
        read_sources_task,
        trigger=CronTrigger(day_of_week=random_day_of_week, hour=random_hour),
        id="read_sources",  # Unique ID for the job
        replace_existing=True,
    )

    scheduler.start()
    logger.debug("Scheduler setup complete.")

    # Gracefully shut down the scheduler when the app stops
    @app.on_event("shutdown")
    def shutdown_scheduler():
        logger.debug("Shutting down scheduler...")
        scheduler.shutdown()
        logger.debug("Scheduler shut down.")
