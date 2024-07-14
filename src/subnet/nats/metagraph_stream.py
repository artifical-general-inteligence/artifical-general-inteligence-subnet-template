import asyncio
import json
import nats
import argparse
import time
import bittensor as bt
from nats.js.errors import KeyNotFoundError


async def get_metagraph_items(metagraph):
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


async def verify_uid_hotkey(uid: str, hotkey: str):
    try:
        nc = await nats.connect("localhost", user='auth', password='auth')
        js = nc.jetstream()
        kv = await js.create_key_value(bucket="metagraph")
        entry = await kv.get(uid)
        json_value = entry.value.decode('utf-8')
        value_dict = json.loads(json_value)
        return value_dict["hotkey"] == hotkey, value_dict
    except KeyNotFoundError:
        return False, None
    finally:
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
        items = await get_metagraph_items(metagraph)

        nc = await nats.connect("localhost", user='auth', password='auth')
        js = nc.jetstream()

        kv = await js.create_key_value(bucket="metagraph")
        for item in items:
            json_item = json.dumps(item)
            await kv.put(str(item["uid"]), json_item.encode('utf-8'))

        time.sleep(12 * 10)


if __name__ == "__main__":
    asyncio.run(run())

## metagraph_stream
# put in proper folder structure
# make microservice
# create pydantic settings class
# create dockerfile

## auth_service
# put in proper folder structure
# make microservice
# create pydantic settings class
# create dockerfile

# create docker compose
# auth_service  depends on metagraph_stream



