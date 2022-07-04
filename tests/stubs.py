from enum import IntEnum
from multiprocessing import Process

from flask import Flask, request
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
def button(*args):
    return {}
def events(*args):
    return {"data": EndPoint.EVENTS + f"{APDUStatus.SUCCESS:x}"}


class SpeculosServerStub:

    def __init__(self):
        self.app = Flask('stub')
        self.app.add_url_rule("/", view_func=root)
        self.app.add_url_rule("/apdu", methods=["GET", "POST"], view_func=apdu)
        self.app.add_url_rule("/button/right", methods=["GET", "POST"], view_func=button)
        self.app.add_url_rule("/button/left", methods=["GET", "POST"], view_func=button)
        self.app.add_url_rule("/button/both", methods=["GET", "POST"], view_func=button)
        self.app.add_url_rule("/events", view_func=events)
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
