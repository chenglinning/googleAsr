#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import logging
import json
import base64
#from utils.log_utils import setup_logging
from google_asr_base64 import recognize_google
import time

"""
TODO: logger module to clean logger code for each file
logging level
asyncoronize
"""

connected = set()


async def ws_server(ws, path):

    connected.add(ws)
    print('current: ')
    print(connected)

    while True:
        try:
            in_data = await ws.recv()
            print(in_data) 
            data = json.loads(in_data)
            out = data
            start = time.time()
            wav = base64.b64decode(data['data']['audio'])
            # frames = wav.getnframes()
            # frate = wav.getframerate()
            # print("duration: {}".format(frames / float(frate)))
            out['data']['result'] = recognize_google(wav)
            stop = time.time()
            out['data']['response_time'] = round(stop - start, 5)
            del out['data']['audio']
            await ws.send(json.dumps(out))
        
        except websockets.exceptions.ConnectionClosed:
            '''
            TODO: Logging.info
            '''
            print('{}: user disconnected'.format(int(time.time())))
            connected.remove(ws)
            print(connected)
            break
            
start_server = websockets.serve(ws_server, 'localhost', 3456)
print('Start listening:')

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

