#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import wave
import json
import datetime
import base64
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

"""
TODO: logger module to clean logger code for each file
logging level
asyncoronize
"""

connected = set()

responses = ''


def init(args):
    global infile, samplewidth, outfile, params

    infile = wave.open(args.infile, 'rb')
    samplewidth = infile.getsampwidth()
    outfile = wave.open(args.outfile, 'wb')
    params = infile.getparams()
    outfile.setparams(params)


def print_response(r):
    for response in r:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:
            # print('Finished: {}'.format(result.is_final))
            # print('Stability: {}'.format(result.stability))
            alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                # print('Confidence: {}'.format(alternative.confidence))
                # print(u'Transcript: {}'.format(alternative.transcript))
                return alternative.transcript


def speech_api(stream):

    client = speech.SpeechClient()

    requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in stream)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
        single_utterance=False)

    res = client.streaming_recognize(streaming_config, requests)

    return res


streams = []
responses = ''


async def consumer(data):
    global streams, responses
    j = json.loads(data)
    streams.append(base64.b64decode(j['data']['audio']))

    # if j['header'][6] == 0:
    #     responses = speech_api(streams)


async def producer():
    await asyncio.sleep(0.1)
    responses = speech_api(streams)
    return print_response(responses)


async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)


async def producer_handler(websocket, path):
    while True:
        message = await producer()
        if message is None:
            break
        else:
            await websocket.send(message)


async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


def main():
    start_server = websockets.serve(handler, 'localhost', 3456)
    print('Start listening:')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
