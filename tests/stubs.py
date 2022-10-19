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
        self.iter = 0
        self.idx = 1

    def button(self, *args):
        path = request.path
        if "right" in path:
            self.idx = self.idx + 1 if (self.idx < 2) else 0
        elif "left" in path:
            self.idx = self.idx - 1 if (self.idx >= 1) else 0
        elif "both" in path:
            if self.idx == 2:
                self.idx = 3
        return {}

    def screenshot(self, *args):
        path = Path(
            __file__).parent.resolve() / "snapshots/nanos/generic" / f"{str(self.idx).zfill(5)}.png"
        if self.iter == 1:
            self.idx = 0
        self.iter = self.iter + 1
        img_temp = Image.open(path)
        iobytes = BytesIO()
        img_temp.save(iobytes, format="PNG")
        return iobytes.getvalue(), 200


def events(*args):
    return {"data": EndPoint.EVENTS + f"{APDUStatus.SUCCESS:x}"}


class SpeculosServerStub:

    def __init__(self):
        actions = Actions()
        self.app = Flask('stub')
        self.app.add_url_rule("/", view_func=root)
        self.app.add_url_rule("/apdu", methods=["GET", "POST"], view_func=apdu)
        self.app.add_url_rule("/button/right", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/button/left", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/button/both", methods=["GET", "POST"], view_func=actions.button)
        self.app.add_url_rule("/events", view_func=events)
        self.app.add_url_rule("/screenshot", methods=["GET"], view_func=actions.screenshot)
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
