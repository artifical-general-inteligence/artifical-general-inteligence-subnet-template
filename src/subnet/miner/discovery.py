import json
import threading
import time
import signal

from substrateinterface import Keypair

from src.subnet.framework.producer_base import ProducerBase
from src.subnet.miner.clients.ollama_cient import OllamaClient


class DiscoveryProducer(ProducerBase):
    def __init__(self, keypair: Keypair, miner_uid: int, ollama_client):
        super().__init__(keypair)
        self.miner_uid = miner_uid
        self.ollama_client = ollama_client
        self.topic = "discovery"

    def publish_discovery(self):
        """
        Load a JSON file and publish its content to a Kafka topic.
        """
        available_locally = self.ollama_client.tags()
        currently_loaded = self.ollama_client.ps()

        message = {
            "available_locally": available_locally,
            "currently_loaded": currently_loaded
        }

        self.produce(self.topic, miner_uid=self.miner_uid, message_objs=message)

    def prepare_message(self, message_objs):
        return json.dumps(message_objs)


# Flag to control the running of the thread
running = True


def publish_discovery_periodically(producer, interval):
    global running
    while running:
        producer.publish_discovery()
        time.sleep(interval)


def start_discovery_producer(keypair: Keypair, miner_uid: int, interval: int):
    producer = DiscoveryProducer(keypair, miner_uid, OllamaClient())
    thread = threading.Thread(target=publish_discovery_periodically, args=(producer, interval))
    thread.start()
    return thread


def signal_handler(signum, frame):
    global running
    running = False


if __name__ == "__main__":
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the discovery consumer with a 10-second interval

    mnemonic = Keypair.generate_mnemonic()
    keypair = Keypair.create_from_mnemonic(mnemonic)

    thread = start_discovery_producer(keypair, 1, 8)

    # Wait for the thread to finish
    thread.join()
