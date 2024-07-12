Given your requirements, the most effective solution would be to use a single topic with log compaction where each miner sends its discovery data. Validators can then consume from this topic to get the latest messages from each miner, ensuring they have the current state of all miners.

### Solution: Single Topic with Log Compaction

#### 1. Create a Kafka Topic with Log Compaction

Create a Kafka topic with log compaction enabled. This ensures that only the latest message for each key (miner ID) is retained.

```bash
kafka-topics.sh --create --topic miner_discoveries --bootstrap-server your_kafka_broker --partitions 10 --replication-factor 3 --config cleanup.policy=compact
```

#### 2. Miner Message Publishing

Each miner should publish its discovery messages to this topic using its miner ID as the key. This ensures Kafka keeps only the latest message per miner ID.

```python
from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'your_kafka_broker'})

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def send_discovery_message(miner_id, message):
    key = str(miner_id)
    value = json.dumps(message)
    producer.produce(
        'miner_discoveries',
        key=key,
        value=value,
        callback=delivery_report
    )
    producer.flush()
```

#### 3. Validator Message Consumption

When a validator joins the cluster, it should consume messages from the `miner_discoveries` topic starting from the earliest offset to build the current state of all miners.

```python
from confluent_kafka import Consumer, KafkaError
import json

consumer_config = {
    'bootstrap.servers': 'your_kafka_broker',
    'group.id': 'validator_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(consumer_config)
consumer.subscribe(['miner_discoveries'])

# Build in-memory structure from messages
in_mem_structure = {}

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        miner_id = msg.key().decode('utf-8')
        discovery_message = json.loads(msg.value().decode('utf-8'))
        in_mem_structure[miner_id] = discovery_message
        print(f'Received message from miner {miner_id}: {discovery_message}')
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Summary

- **Topic Configuration:** A single topic with log compaction (`miner_discoveries`) ensures that only the latest message per miner ID is retained.
- **Publishing:** Miners send discovery messages with their miner ID as the key, ensuring Kafka can compact messages correctly.
- **Consumption:** Validators consume from the topic to build an in-memory structure of the latest state for each miner.

### Considerations

- **Log Compaction Delay:** Be aware that log compaction is not instantaneous. There might be a slight delay before older messages are compacted away.
- **Partition Count:** Ensure you have enough partitions to handle the throughput from all miners. Each partition can handle multiple miners, but having too few partitions might lead to performance bottlenecks.
- **Error Handling:** Implement robust error handling in both the producer and consumer to manage potential issues during message production and consumption.

This solution ensures that validators can easily pick the latest messages for each miner, providing the current state of all miners efficiently.