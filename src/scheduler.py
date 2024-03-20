from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.products.tasks import publish_products_task

scheduler = AsyncIOScheduler()

def setup_scheduler(app):
    # Schedule the task to run three times a day at 9 AM, 3 PM, and 9 PM
    scheduler.add_job(
        publish_products_task,
        trigger=CronTrigger(hour="9,15,21"),
        id="publish_products",  # Unique ID for the job
        replace_existing=True,
    )
    scheduler.start()

    # Gracefully shut down the scheduler when the app stops
    @app.on_event("shutdown")
    def shutdown_scheduler():
        scheduler.shutdown()
