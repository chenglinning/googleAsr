#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import datetime
import wave
import json
import base64
#from utils.log_utils import setup_logging
from google_asr_base64 import recognize_google
from google_asr_base64 import UnknownValueError
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

    with wave.open(f"output/{datetime.datetime.now():%Y-%m-%dT%H%M%S}.wav", mode='wb') as f:
        f.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        while True:
            try:
                in_data = await ws.recv()
                print(in_data)
                data = json.loads(in_data)
    #            start = time.time()
    #            wav = base64.b64decode(data['data']['audio'])

                if 'audio' in data['data']:
                    chunk = ''.join(data['data']['audio'])
                else:
                    chunk = ''
                f.writeframesraw(base64.b64decode(chunk))

                # try:
                #     out['data']['result'] = recognize_google(wav)
                # except UnknownValueError:
                #     out['data']['result'] = 'Unknown'

    #            stop = time.time()
    #            out['data']['response_time'] = round(stop - start, 5)
    #            del out['data']['audio']
                await ws.send("Done")

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

