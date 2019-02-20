import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class UnknownValueError(Exception): pass
class RequestError(Exception): pass
class UnknownValueError(Exception): pass
class AudioFormatNotSupportedError(Exception):pass


def recognize_google(audio_data, rate=16000, key=None, language="en-US", show_all=False):
    if key is None:
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
    url = "http://www.google.com/speech-api/v2/recognize?{0}".format(urlencode({
            "client": "chromium",
            "lang": language,
            "key": key,
        }))

    request = Request(url, data=audio_data, headers={"Content-Type": "audio/l16; rate={0}".format(rate)})
    try:
        response = urlopen(request)
    except HTTPError as e:
        raise RequestError("recognition request failed: {0}".format(getattr(e, "reason", "status {0}".format(e.code)))) # use getattr to be compatible with Python 2.6
    except URLError as e:
        raise RequestError("recognition connection failed: {0}".format(e.reason))
    response_text = response.read().decode("utf-8")
    print(response_text)

    # ignore any blank blocks
    actual_result = []
    for line in response_text.split("\n"):
        if not line:
            continue
        result = json.loads(line)["result"]
        if len(result) != 0:
            actual_result = result[0]
            break

    # return results
    if show_all: return actual_result
    if "alternative" not in actual_result: raise UnknownValueError()
    for entry in actual_result["alternative"]:
        if "transcript" in entry:
            return entry["transcript"]
    raise UnknownValueError() # no transcriptions available


if __name__ == '__main__':
    with open("data/Kikago_20190216_154159_NC.wav", 'rb') as speech:
        speech_content = speech.read()

    start = time.time()
    recognize_google(speech_content)
    end = time.time()
    print('response time: {}'.format(end - start))
