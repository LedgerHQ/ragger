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
from ragger.backend import BackendInterface
from ragger.firmware import Firmware
from .positions import POSITIONS


class _UseCase:

    def __init__(self, client: BackendInterface, firmware: Firmware):
        self._client = client
        self._firmware = firmware

    @property
    def client(self) -> BackendInterface:
        return self._client

    @property
    def firmware(self) -> Firmware:
        return self._firmware

    @property
    def positions(self):
        return POSITIONS[str(self.__class__.__name__)]


class UseCaseHome(_UseCase):

    def info(self):
        self.client.finger_touch(*self.positions["info"])

    def settings(self):
        self.client.finger_touch(*self.positions["settings"])

    def quit(self):
        self.client.finger_touch(*self.positions["quit"])


class UseCaseHomeExt(UseCaseHome):

    def action(self):
        self.client.finger_touch(*self.positions["action"])


class UseCaseSettings(_UseCase):

    def single_page_exit(self):
        self.client.finger_touch(*self.positions["single_page_exit"])

    def multi_page_exit(self):
        self.client.finger_touch(*self.positions["multi_page_exit"])

    def previous(self):
        self.client.finger_touch(*self.positions["previous"])

    def next(self):
        self.client.finger_touch(*self.positions["next"])


class UseCaseSubSettings(_UseCase):

    def exit(self):
        self.client.finger_touch(*self.positions["exit"])

    def previous(self):
        self.client.finger_touch(*self.positions["previous"])

    def next(self):
        self.client.finger_touch(*self.positions["next"])


class UseCaseChoice(_UseCase):

    def confirm(self):
        self.client.finger_touch(*self.positions["confirm"])

    def reject(self):
        self.client.finger_touch(*self.positions["reject"])


class UseCaseStatus(_UseCase):

    def dismiss(self):
        self.client.finger_touch(*self.positions["dismiss"])


class UseCaseReview(_UseCase):

    def tap(self):
        self.client.finger_touch(*self.positions["tap"])

    def previous(self):
        self.client.finger_touch(*self.positions["previous"])

    def reject(self):
        self.client.finger_touch(*self.positions["reject"])

    def confirm(self):
        # SDK needs at least 1.5s for long press.
        self.client.finger_touch(*self.positions["confirm"], 1.5)


class UseCaseViewDetails(_UseCase):

    def exit(self):
        self.client.finger_touch(*self.positions["exit"])

    def previous(self):
        self.client.finger_touch(*self.positions["previous"])

    def next(self):
        self.client.finger_touch(*self.positions["next"])


class UseCaseAddressConfirmation(_UseCase):

    def tap(self):
        self.client.finger_touch(*self.positions["tap"])

    def exit_qr(self):
        self.client.finger_touch(*self.positions["exit_qr"])

    def confirm(self):
        self.client.finger_touch(*self.positions["confirm"])

    def cancel(self):
        self.client.finger_touch(*self.positions["cancel"])
