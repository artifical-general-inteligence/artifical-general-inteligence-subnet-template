import asyncio
import json
import signal
import sys
from nats.aio.client import Client as NATS

def handle_sigterm(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()

async def main():
    nc = NATS()

    async def error_cb(e):
        print(f"Error: {e}")

    async def closed_cb():
        print("Connection to NATS closed.")

    async def reconnected_cb():
        print(f"Reconnected to NATS at {nc.connected_url.netloc}")

    options = {
        "servers": ["nats://127.0.0.1:4222"],
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb
    }

    await nc.connect(**options)

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Received a message on '{subject} {reply}': {data}")

        auth_request = json.loads(data)
        connect_opts = auth_request.get("connect_opts", {})
        user = connect_opts.get("user")
        password = connect_opts.get("pass")

        response = {}
        if user == "valid_user" and password == "valid_pass":
            response["jwt"] = "dummy-jwt"
            response["error"] = None
        else:
            response["jwt"] = None
            response["error"] = "Invalid user credentials"

        await nc.publish(reply, json.dumps(response).encode())

    await nc.subscribe("$SYS.REQ.USER.AUTH", cb=message_handler)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: handle_sigterm(loop))

    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
