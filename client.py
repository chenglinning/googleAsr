#!/usr/bin/env python

# WS client example

import asyncio
import websockets
import json
import time
import base64

quest = {
            'header': [1111, 0, 1000, int(time.time()), 3, 0],
            'data': {
                'audio': None
            }
}


async def hello():
    async with websockets.connect(
            'ws://localhost:8765') as websocket:

        start = time.time()
        with open("data/test_message.wav", "rb") as speech:
            quest['data']['audio'] = base64.b64encode(speech.read()).decode('utf-8')
        await websocket.send(json.dumps(quest))

        greeting = await websocket.recv()
        stop = time.time()
        print(f"< {greeting}")
        print('round trip time: {}'.format(round(stop - start, 5)))

asyncio.get_event_loop().run_until_complete(hello())
