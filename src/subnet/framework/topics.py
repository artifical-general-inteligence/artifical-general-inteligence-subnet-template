from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from .config import settings


def create_topic(topic_name, num_partitions=1, replication_factor=1):
    admin_client = AdminClient({'bootstrap.servers': settings.kafka_bootstrap_servers})

    topic_list = admin_client.list_topics().topics
    if topic_name in topic_list:
        print(f"Topic '{topic_name}' already exists.")
        return

    new_topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
    fs = admin_client.create_topics([new_topic])

    for topic, f in fs.items():
        try:
            f.result()
            print(f"Topic '{topic}' created")
        except KafkaException as e:
            print(f"Failed to create topic '{topic}': {e}")