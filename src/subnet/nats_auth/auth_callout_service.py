import asyncio
import json
from aiohttp import web

async def authenticate(request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')

    with open('users.json', 'r') as f:
        users = json.load(f)

    user = users.get(username)
    if user and user.get('pass') == password:
        return web.json_response({'status': 'ok', 'account': user.get('account')})
    else:
        return web.json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)

async def start_auth_callout_service():
    app = web.Application()
    app.router.add_post('/auth', authenticate)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8085)
    await site.start()
    print("Auth callout service started on http://localhost:8085")

    while True:
        await asyncio.sleep(3600)  # Keep the service running

if __name__ == '__main__':
    asyncio.run(start_auth_callout_service())
