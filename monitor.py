import os
from celery import Celery
from flower.command import FlowerCommand
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv('REDIS_URL')

def create_celery_app():
    """Create Celery app with Redis configuration"""
    app = Celery('worker',
                 broker=redis_url,
                 backend=redis_url)
    return app

def start_flower():
    """Start Flower monitoring"""
    app = create_celery_app()
    logger.info("Starting Flower with Redis URL: %s", redis_url)

    flower = FlowerCommand(
        broker=redis_url,
        address='0.0.0.0',
        port=int(os.getenv('PORT', '5555')),
        basic_auth=os.getenv('FLOWER_AUTH'),
        url_prefix=os.getenv('FLOWER_URL_PREFIX', '')
    )
    flower.execute_from_commandline()

if __name__ == '__main__':
    start_flower()