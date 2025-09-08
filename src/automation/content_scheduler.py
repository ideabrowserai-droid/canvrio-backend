"""
Canvrio Content Scheduler
Automatically refreshes content every 4 hours during business days
"""

import schedule
import time
import logging
from datetime import datetime
from content_aggregator import ContentAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def refresh_content():
    """Run content aggregation"""
    try:
        logger.info("Starting scheduled content refresh...")
        aggregator = ContentAggregator()
        total_items = aggregator.run_aggregation()
        logger.info(f"Scheduled refresh complete. Processed {total_items} items.")
        return total_items
    except Exception as e:
        logger.error(f"Error during scheduled refresh: {e}")
        return 0

def is_business_hours():
    """Check if current time is during business hours (9 AM - 9 PM)"""
    current_hour = datetime.now().hour
    return 9 <= current_hour <= 21

def conditional_refresh():
    """Run refresh only during business hours"""
    if is_business_hours():
        refresh_content()
    else:
        logger.info("Outside business hours - skipping refresh")

def setup_schedule():
    """Set up content refresh schedule"""
    # Business days: Every 4 hours during business hours (9 AM - 9 PM)
    schedule.every(4).hours.do(conditional_refresh)
    
    # Weekend: Every 8 hours (less frequent)
    schedule.every().saturday.at("10:00").do(refresh_content)
    schedule.every().saturday.at("18:00").do(refresh_content)
    schedule.every().sunday.at("10:00").do(refresh_content)
    schedule.every().sunday.at("18:00").do(refresh_content)
    
    logger.info("Content refresh schedule configured:")
    logger.info("- Business days: Every 4 hours (9 AM - 9 PM)")
    logger.info("- Weekends: 10 AM and 6 PM")

def run_scheduler():
    """Run the content scheduler"""
    logger.info("Starting Canvrio Content Scheduler...")
    setup_schedule()
    
    # Run initial content refresh
    refresh_content()
    
    # Keep running and check for scheduled jobs
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Content scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    run_scheduler()