import json
from loguru import logger
from substrateinterface import Keypair

from .config import settings
from abc import ABC, abstractmethod
from confluent_kafka import Producer, KafkaError
from .messages import sign_message


class ProducerBase(ABC):
    def __init__(self, keypair: Keypair):
        self.producer = Producer({
            'bootstrap.servers': settings.kafka_bootstrap_servers
        })
        self.keypair= keypair

    def produce(self, topic, miner_uid: int, message_objs):
        prepared_message = self.prepare_message(message_objs)
        signature, public_key = sign_message(self.keypair, prepared_message)
        message_payload = {
            "message": prepared_message,
            "signature": signature,
            "public_key": public_key
        }
        self.producer.produce(topic, key=str(miner_uid), value=json.dumps(message_payload))
        self.producer.flush()

        logger.info(f"Message payload published: {message_payload}")

    @abstractmethod
    def prepare_message(self, message_objs):
        """
        Prepare the message for sending. This method needs to be implemented by subclasses.
        """
        pass
