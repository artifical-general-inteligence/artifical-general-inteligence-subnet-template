import json
from loguru import logger
from .config import settings
from abc import ABC, abstractmethod
from confluent_kafka import Producer, KafkaError
from .messages import load_private_key, sign_message


class ProducerBase(ABC):
    def __init__(self, key):
        self.producer = Producer({
            'bootstrap.servers': settings.kafka_bootstrap_servers
        })
        self.key = key

    def produce(self, topic, message_objs):
        prepared_message = self.prepare_message(message_objs)
        signature, public_key = sign_message(self.key, prepared_message)
        message_payload = {
            "message": prepared_message,
            "signature": signature,
            "public_key": public_key
        }
        self.producer.produce(topic, json.dumps(message_payload))
        self.producer.flush()

        logger.info(f"Message payload published: {message_payload}")

    @abstractmethod
    def prepare_message(self, message_objs):
        """
        Prepare the message for sending. This method needs to be implemented by subclasses.
        """
        pass
