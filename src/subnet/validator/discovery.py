import threading
from loguru import logger
from pydantic import ValidationError
from src.subnet.framework.consumer_base import ConsumerBase


class DiscoveryConsumer(ConsumerBase):
    def __init__(self):
        super().__init__(group_id='discovery_group', topic='discovery')

    def process_message(self, message: dict):
        try:
            logger.info(f"Inserting discovery into database: {message}")
        except ValidationError as e:
            logger.info(f"Validation error: {e}")


def start_discovery_consumer():
    consumer = DiscoveryConsumer()
    thread = threading.Thread(target=consumer.consume)
    thread.start()
    return thread


# Usage example:
if __name__ == "__main__":
    thread = start_discovery_consumer()
    logger.info("Discovery consumer started")
    thread.join()
