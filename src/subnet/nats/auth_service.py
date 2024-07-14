import asyncio
import json
import signal
import sys

import jwt
from nats.aio.client import Client as NATS

from src.subnet.framework.messages import verify_message
from src.subnet.nats import metagraph_stream


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
        "reconnected_cb": reconnected_cb,
        "user": "auth",
        "password": "auth",
    }

    await nc.connect(**options)

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        try:
            data = msg.data.decode()

            # Decode JWT without verifying first to extract user and password
            auth_request = jwt.decode(data, options={"verify_signature": False})
            connect_opts = auth_request.get("nats", {}).get("connect_opts", {})

            user_identity = connect_opts.get("user")
            user_identity_dict = json.loads(user_identity)
            hotkey = user_identity_dict.get("hotkey")
            uid = user_identity_dict.get("uid")

            password = connect_opts.get("pass")
            password_dict = json.loads(password)
            signature = password_dict.get("signature")
            public_key = password_dict.get("public_key")

            response = {}

            if not verify_message(public_key, user_identity, signature):
                response["jwt"] = None
                response["error"] = "Invalid user credentials"
            else:
                is_valid, item = await metagraph_stream.verify_uid_hotkey(uid, hotkey)
                if is_valid:
                    xkey_seed = "xkey_seed"
                    claims = {
                        "user": user_identity,
                        "role": item["role"]
                    }
                    response["jwt"] = jwt.encode(claims, xkey_seed, algorithm="HS256")
                else:
                    response["jwt"] = None
                    response["error"] = "Invalid user credentials"

            await nc.publish(reply, json.dumps(response).encode())

        except UnicodeDecodeError:
            print(f"Failed to decode message data on '{subject} {reply}'")
            response = {"error": "Invalid message encoding"}
            await nc.publish(reply, json.dumps(response).encode())
        except json.JSONDecodeError:
            print(f"Failed to parse JSON on '{subject} {reply}'")
            response = {"error": "Invalid JSON format"}
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
