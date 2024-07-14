import asyncio
import json

import nats
import numpy as np
import argparse
import time
import bittensor as bt
from loguru import logger
import random

from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from nats.js.api import StreamConfig, RetentionPolicy


async def get_miners(metagraph):
    results = []
    for uid in range(metagraph.n.item()):
        results.append({
            "uid": uid,
            "ip": metagraph.neurons[uid].axon_info.ip,
            "port": metagraph.neurons[uid].axon_info.port,
            "coldkey": metagraph.neurons[uid].axon_info.coldkey,
            "hotkey": metagraph.neurons[uid].axon_info.hotkey,
            "role":  metagraph.neurons[uid].axon_info.ip == '0.0.0.0' and "validator" or "miner"
        })
        return results


async def configure():
    try:
        nc = await nats.connect("localhost", user='auth', password='auth')
        js = nc.jetstream()
        stream_name = "metagraph"
        subject_name = "metagraph.*"
        stream_config = StreamConfig(
            name=stream_name,
            subjects=[subject_name],
            retention=RetentionPolicy.LIMITS,
            max_msgs_per_subject=1,
        )
        ack = await js.add_stream(config=stream_config)
        print(f"Stream '{stream_name}' with subject '{subject_name}' configured successfully.")
        print("Stream configuration ACK:", ack)
    except ErrConnectionClosed:
        print("Connection closed prematurely.")
    except ErrTimeout:
        print("Request timed out.")
    except ErrNoServers:
        print("No NATS servers available.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if nc.is_connected:
            await nc.close()


async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--netuid', type=int, default=1)
    parser.add_argument('--subtensor.chain_endpoint', type=str, default='ws://127.0.0.1:9946')
    parser.add_argument('--subtensor.network', type=str, default='finney')

    config = bt.config(parser)
    bt.subtensor.add_args(parser)
    subtensor = bt.subtensor(config)

    while True:
        metagraph = subtensor.metagraph(config.netuid)
        metagraph.sync(subtensor=subtensor)
        miners = await get_miners(metagraph)

        nc = await nats.connect("localhost", user='auth', password='auth')
        js = nc.jetstream()
        subject_base = "metagraph"

        for miner in miners:
            uid = miner["uid"]
            subject_name = f"{subject_base}.{uid}"
            message = json.dumps(miner).encode('utf-8')
            ack = await js.publish(subject_name, message)
            print(f"Published to {subject_name}, message: {message}, ack: {ack}")

        time.sleep(12 * 10)


if __name__ == "__main__":
    asyncio.run(configure())
    asyncio.run(run())





