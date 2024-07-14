import asyncio
import json

import nats
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from nats.js.api import StreamConfig, RetentionPolicy
from substrateinterface import Keypair

from src.subnet.framework.messages import sign_message


async def configure():
    try:
        nc = await nats.connect("localhost", user='auth', password='auth')
        js = nc.jetstream()
        stream_name = "miner_discovery"
        subject_name = "miner.discovery.*"
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


async def get_messages():
    nc = await nats.connect("localhost", user='auth', password='auth')
    js = nc.jetstream()
    subject_base = "miner.discovery.*"
    sub = await js.subscribe(subject_base)
    async for msg in sub.messages:
        print(f"Received a message on '{msg.subject}': {msg.data.decode()}")
    await nc.close()


async def main():

    mnemonic = Keypair.generate_mnemonic()
    keypair = Keypair.create_from_mnemonic(mnemonic)
    user_identity_params = {
        "uid": 1,
        "hotkey":  keypair.ss58_address,
    }

    user_identity = json.dumps(user_identity_params)

    signature, public_key = sign_message(keypair, user_identity)
    password_params = {
        "signature": signature,
        "public_key": public_key
    }
    password = json.dumps(password_params)

    nc = await nats.connect("localhost", user=user_identity, password=password)

    js = nc.jetstream()
    subject_base = "miner.discovery"

    for i in range(1, 2):
        subject_name = f"{subject_base}.{i}"

        message_content = {"text": f"some message here {i}"}
        message = json.dumps(message_content).encode('utf-8')

        ack = await js.publish(subject_name, message)
        print(f"Published to {subject_name}, message: {message}, ack: {ack}")

    await nc.close()

if __name__ == '__main__':
    asyncio.run(configure())
    asyncio.run(main())
    asyncio.run(get_messages())