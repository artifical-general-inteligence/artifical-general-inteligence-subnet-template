import json
from loguru import logger
from pydantic import ValidationError
from .config import settings
from abc import ABC, abstractmethod
from confluent_kafka import Consumer, KafkaError
from .messages import load_public_key, verify_signature, verify_message


class ConsumerBase(ABC):
    def __init__(self, group_id, topic):
        self.consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([topic])

    def consume(self):
        try:
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
            message = message_payload_dict.get("message")
            signature = message_payload_dict.get("signature")
            public_key = load_public_key(message_payload_dict.get("public_key"))

            if not verify_message(public_key, message, signature):
                logger.error("Invalid signature for message: {message}")
                return
            message_dict = json.loads(message)
            self.process_message(message_dict)
        except ValidationError as e:
            logger.info(f"Validation error: {e}")
        except json.JSONDecodeError as e:
            logger.info(f"Failed to decode message: {e}")

    @abstractmethod
    def process_message(self, message):
        pass
