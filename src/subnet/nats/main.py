import asyncio

import nats
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from nats.js.api import StreamConfig, RetentionPolicy


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
    nc = await nats.connect("localhost", user='auth', password='auth')
    js = nc.jetstream()
    subject_base = "miner.discovery"

    for i in range(1, 11):
        subject_name = f"{subject_base}.{i}"
        message = f"some message here {i}".encode('utf-8')
        ack = await js.publish(subject_name, message)
        print(f"Published to {subject_name}, ack: {ack}")

    await nc.close()

if __name__ == '__main__':
    asyncio.run(configure())
    #asyncio.run(main())
    #asyncio.run(get_messages())