import os
from celery import Celery
from flower.app import Flower
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv('REDIS_URL')

def create_celery_app():
    """Create Celery app with Redis configuration"""
    # Parse Redis URL
    parsed_url = urlparse(redis_url)
    
    # Configure Celery broker URL explicitly
    broker_url = f'redis://{parsed_url.hostname}:{parsed_url.port}'
    if parsed_url.username and parsed_url.password:
        broker_url = f'redis://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}'
    
    logger.info(f"Connecting to broker at: {broker_url}")
    
    app = Celery('worker',
                 broker=broker_url,
                 backend=broker_url,
                 broker_connection_retry=True,
                 broker_connection_max_retries=10)
    
    # Configure Celery to use Redis
    app.conf.update(
        broker_transport_options={
            'visibility_timeout': 3600,
            'socket_timeout': 30,
            'socket_connect_timeout': 30,
        },
        result_backend=broker_url,
        redis_max_connections=20,
        task_serializer='json',
        accept_content=['json']
    )
    
    return app

def start_flower():
    """Start Flower monitoring"""
    app = create_celery_app()
    logger.info("Starting Flower with Redis URL: %s", redis_url)

    # Create Flower app
    flower = Flower(
        urlconf='flower.urls',
        app=app,
        address='0.0.0.0',
        port=int(os.getenv('PORT', '5555')),
        auth=os.getenv('FLOWER_AUTH'),
        url_prefix=os.getenv('FLOWER_URL_PREFIX', ''),
        broker_api=redis_url  # Add broker API URL
    )
    
    # Start Flower
    flower.start()

if __name__ == '__main__':
    start_flower()