from enum import IntEnum
from io import BytesIO
from multiprocessing import Process
from pathlib import Path

from flask import Flask, request
from PIL import Image
from requests import get
from requests.exceptions import ConnectionError


class APDUStatus(IntEnum):
    SUCCESS = 0x9000
    ERROR = 0x8000


class EndPoint:
    ROOT = "01"
    APDU = "02"
    EVENTS = "03"


class Events:
    back = [{"text": "Back", "x": 51, "y": 19}]
    info = [{
        "text": "Boilerplate App",
        "x": 20,
        "y": 3
    }, {
        "text": "(c) 2020 Ledger",
        "x": 26,
        "y": 17
    }]
    home = [{"text": "Boilerplate", "x": 41, "y": 3}, {"text": "is ready", "x": 41, "y": 17}]
    version = [{"text": "Version", "x": 43, "y": 3}, {"text": "1.0.1", "x": 52, "y": 17}]
    about = [{"text": "About", "x": 47, "y": 19}]
    indexed = [home, version, about, info, back]


# can't use lambdas: Flask stores functions using their names (and lambdas have none, so they'll
# override each other)
# Returned value must be a JSON, embedding a 'data' field with an hexa string ending with 9000 for
# success
def root(*args):
    return {"data": EndPoint.ROOT + f"{APDUStatus.SUCCESS:x}"}


def apdu(*args):
    apdu = bytes.fromhex(request.get_json().get("data", "00"))
    status = f"{APDUStatus.SUCCESS:x}" if apdu[0] == 0x00 else f"{APDUStatus.ERROR:x}"
    return {"data": EndPoint.APDU + status}


class Actions:

    def __init__(self):
        self.idx = 0

    def button(self, *args):
        path = request.path
        if "right" in path:
            if self.idx == 2:
                self.idx = 0
            elif self.idx == 4:
                self.idx = 3
            else:
                self.idx = self.idx + 1
        elif "left" in path:
            if self.idx == 0:
                self.idx = 2
            elif self.idx == 3:
                self.idx = 4
            else:
                self.idx = self.idx - 1
        elif "both" in path:
            if self.idx == 2:
                self.idx = 3
            if self.idx == 4:
                self.idx = 0

        return {}

    def events(self, *args):
        return {"events": Events.indexed[self.idx]}, 200

    def screenshot(self, *args):
        path = Path(
            __file__).parent.resolve() / "snapshots/nanos/generic" / f"{str(self.idx).zfill(5)}.png"
        img_temp = Image.open(path)
        iobytes = BytesIO()
        img_temp.save(iobytes, format="PNG")
        return iobytes.getvalue(), 200

    def ticker(self, *args):
        return {}


class SpeculosServerStub:

    def __init__(self):
        actions = Actions()
        self.app = Flask('stub')
        self.app.add_url_rule("/", view_func=root)
        self.app.add_url_rule("/apdu", methods=["GET", "POST"], view_func=apdu)
        self.app.add_url_rule("/button/right", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/button/left", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/button/both", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/events", view_func=actions.events)
        self.app.add_url_rule("/screenshot", methods=["GET"], view_func=actions.screenshot)
        self.app.add_url_rule("/ticker", methods=["GET", "POST"], view_func=actions.ticker)
        self.process = None

    def __enter__(self):
        self.process = Process(target=self.app.run)
        self.process.start()
        started = False
        while not started:
            try:
                get("http://127.0.0.1:5000")
                started = True
            except ConnectionError:
                pass

    def __exit__(self, *args, **kwargs):
        self.process.terminate()
        self.process.join()
        self.process.close()
        self.process = None
