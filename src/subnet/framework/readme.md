- configure perseistent discovery topic with compact mode

```bash
kafka-topics.sh --create --topic miner_discoveries --bootstrap-server your_kafka_broker --partitions 10 --replication-factor 3 --config cleanup.policy=compact
```

miner --> publish discovery to kafka
kafka discovery key  == miner uid
compact param means only the latest discovery will be stored in kafka

valdiator will always pull the latest discovery from kafka  so it can rebuild
its data