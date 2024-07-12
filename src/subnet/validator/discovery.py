import json
from datetime import time

from loguru import logger
from pydantic import ValidationError
from abc import ABC, abstractmethod
from confluent_kafka import Consumer, KafkaError
import threading

from src.subnet.framework.config import settings
from src.subnet.framework.messages import verify_message


class DiscoveryConsumer(ABC):
    def __init__(self):
        self.topic = 'discovery'
        self.group_id = 'discovery_group'
        self.discovery_data = {}
        self.lock = threading.Lock()
        self.consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })

    def consume(self):
        try:
            self.consumer.subscribe([self.topic])

            while True:
                message_payload = self.consumer.poll(1.0)
                if message_payload is None:
                    continue
                if message_payload.error():
                    if message_payload.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(message_payload.error())
                        break

                self.preprocess_message(message_payload.value().decode('utf-8'))
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        finally:
            self.consumer.close()

    def preprocess_message(self, message_payload):
        try:
            logger.info(f"Preprocessing message payload {message_payload}")
            message_payload_dict = json.loads(message_payload)

            public_key = message_payload_dict.get("public_key")
            signature = message_payload_dict.get("signature")
            message = message_payload_dict.get("message")

            if not verify_message(public_key, message, signature):
                logger.error("Invalid signature for message: {message}")
                return
            message_dict = json.loads(message)

            key = message_dict.get("key")
            if key:
                with self.lock:
                    self.discovery_data[key] = message_dict

        except ValidationError as e:
            logger.info(f"Validation error: {e}")
        except json.JSONDecodeError as e:
            logger.info(f"Failed to decode message: {e}")

    def get_discovery_data(self):
        with self.lock:
            return self.discovery_data.copy()


def start_discovery_consumer():
    consumer = DiscoveryConsumer()
    thread = threading.Thread(target=consumer.consume)
    thread.start()
    return thread


def periodic_print(consumer):
    while True:
        data = consumer.get_discovery_data()
        logger.info(f"Discovery data: {data}")
        time.sleep(8)


if __name__ == "__main__":
    consumer, thread = start_discovery_consumer()
    logger.info("Discovery consumer started")

    # Start periodic printing in a separate thread
    print_thread = threading.Thread(target=periodic_print, args=(consumer,))
    print_thread.start()

    # Wait for consumer thread to finish (it won't in this example)
    thread.join()
    print_thread.join()
