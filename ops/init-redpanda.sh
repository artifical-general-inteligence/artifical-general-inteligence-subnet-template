#!/bin/bash

# Wait for Redpanda to be ready
sleep 5
rpk topic create discovery --brokers=redpanda:9092 --config="cleanup.policy=compact,delete"

# Create the receipts topic with a retention period of 1 month (2592000000 ms)
rpk topic create receipts --brokers=redpanda:9092 --config="retention.ms=2592000000"

echo "Topics created."