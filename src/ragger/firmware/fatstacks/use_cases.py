"""
   Copyright 2022 Ledger SAS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from time import sleep

from ragger.backend import BackendInterface
from ragger.firmware import Firmware
from .positions import POSITIONS_BY_SDK


class _UseCase:

    def __init__(self, client: BackendInterface, firmware: Firmware):
        self._client = client
        assert firmware.semantic_version in POSITIONS_BY_SDK, \
            f"This firmware {firmware} is not compatible with layouts"
        self._firmware = firmware

    @property
    def client(self) -> BackendInterface:
        return self._client

    @property
    def firmware(self) -> Firmware:
        return self._firmware

    @property
    def positions(self):
        return POSITIONS_BY_SDK[self._firmware.semantic_version][str(self.__class__.__name__)]


class UseCaseHome(_UseCase):

    def info(self):
        self.client.finger_touch(*self.positions["info"])

    def settings(self):
        self.client.finger_touch(*self.positions["settings"])

    def quit(self):
        self.client.finger_touch(*self.positions["quit"])


class UseCaseSettings(_UseCase):

    def exit(self):
        self.client.finger_touch(*self.positions["exit"])

    def back(self):
        self.client.finger_touch(*self.positions["back"])

    def next(self):
        self.client.finger_touch(*self.positions["next"])


class UseCaseChoice(_UseCase):

    def confirm(self):
        self.client.finger_touch(*self.positions["confirm"])

    def reject(self):
        self.client.finger_touch(*self.positions["reject"])


class UseCaseStatus(_UseCase):

    def wait(self):
        sleep(3)


class UseCaseReview(_UseCase):

    def tap(self):
        self.client.finger_touch(*self.positions["tap"])

    def back(self):
        self.client.finger_touch(*self.positions["back"])

    def reject(self):
        self.client.finger_touch(*self.positions["reject"])

    def confirm(self):
        self.client.finger_touch(*self.positions["confirm"], 2)


class UseCaseViewDetails(_UseCase):

    def exit(self):
        self.client.finger_touch(*self.positions["exit"])

    def back(self):
        self.client.finger_touch(*self.positions["back"])

    def next(self):
        self.client.finger_touch(*self.positions["next"])


class UseCaseAddressConfirmation(_UseCase):

    def show_qr(self):
        self.client.finger_touch(*self.positions["show_qr"])

    def exit_qr(self):
        self.client.finger_touch(*self.positions["exit_qr"])

    def confirm(self):
        self.client.finger_touch(*self.positions["confirm"])

    def cancel(self):
        self.client.finger_touch(*self.positions["cancel"])
