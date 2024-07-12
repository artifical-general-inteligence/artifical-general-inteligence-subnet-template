Delete all topics

```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic delete discovery --brokers=redpanda:9092"
```

Create discovery with cleanup.policy='compact' retention.ms='60000' segment.ms='60000'
```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic create discovery --brokers=redpanda:9092 --partitions=1"
```
Configure topic (wait some time before running the next commands)
```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic alter-config discovery --brokers=redpanda:9092 --set cleanup.policy='compact'"
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic alter-config discovery --brokers=redpanda:9092 --set retention.ms='604800000'"  # Set retention to 1 week (or adjust as needed)
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic alter-config discovery --brokers=redpanda:9092 --set segment.ms='60000'"  # Set segment time to 1 minute to trigger frequent log cleanup
```

Get discovery topic config
```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic describe discovery --brokers=redpanda:9092"
```

Consume messages from discovery topic
```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic consume discovery --brokers=redpanda:9092 --offset=0"
```

## --------------------------
 Create receipts topic with 30 days retention

```bash

```bash
docker exec -it ops-redpanda-1 /bin/bash -c "rpk topic create receipts --brokers=redpanda:9092 --config="retention.ms=2592000000""
````