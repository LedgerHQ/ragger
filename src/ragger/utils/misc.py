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
from typing import Optional, Tuple, List
from pathlib import Path
from ragger.error import ExceptionRAPDU


def app_path_from_app_name(app_dir: Path, app_name: str, device: str) -> Path:
    """
    Builds an application ELF path according to a directory, an application name
    and a device name.
    The resulting path will be formatted like:
    ``<directory>/<application name>_<device name>.elf``
    Example: ``tests/elfs/exchange_nanox.elf``
    The directory and resulting path existence are checked.
    :param app_dir: The directory where the application ELF is
    :type app_dir: Path
    :param app_name: The name of the application
    :type app_name: str
    :param device: The device type name (ex: 'nanos', 'nanosp', ...)
    :type device: str
    """
    assert app_dir.is_dir(), f"{app_dir} is not a directory"
    app_path = app_dir / (app_name + "_" + device + ".elf")
    assert app_path.is_file(), f"{app_path} must exist"
    return app_path


def _is_root(path_to_check: Path) -> bool:
    return (path_to_check).resolve() == Path("/").resolve()


def find_project_root_dir(origin: Path) -> Path:
    project_root_dir = origin
    while not _is_root(project_root_dir) and not (project_root_dir / ".git").resolve().is_dir():
        project_root_dir = project_root_dir.parent
    if _is_root(project_root_dir):
        raise ValueError("Could not find project top directory")
    return project_root_dir


def prefix_with_len(to_prefix: bytes) -> bytes:
    return len(to_prefix).to_bytes(1, byteorder="big") + to_prefix


def create_currency_config(main_ticker: str,
                           application_name: str,
                           sub_coin_config: Optional[Tuple[str, int]] = None) -> bytes:
    sub_config: bytes = b""
    if sub_coin_config is not None:
        sub_config = prefix_with_len(sub_coin_config[0].encode())
        sub_config += sub_coin_config[1].to_bytes(1, byteorder="big")
    coin_config: bytes = b""
    for element in [main_ticker.encode(), application_name.encode(), sub_config]:
        coin_config += prefix_with_len(element)
    return coin_config


def split_message(message: bytes, max_size: int) -> List[bytes]:
    return [message[x:x + max_size] for x in range(0, len(message), max_size)]


def get_current_app_name_and_version(backend):
    try:
        response = backend.exchange(
            cla=0xB0,  # specific CLA for BOLOS
            ins=0x01,  # specific INS for get_app_and_version
            p1=0,
            p2=0).data
        offset = 0

        format_id = response[offset]
        offset += 1
        assert format_id == 1

        app_name_len = response[offset]
        offset += 1
        app_name = response[offset:offset + app_name_len].decode("ascii")
        offset += app_name_len

        version_len = response[offset]
        offset += 1
        version = response[offset:offset + version_len].decode("ascii")
        offset += version_len

        if app_name != "BOLOS":
            flags_len = response[offset]
            offset += 1
            _ = response[offset:offset + flags_len]
            offset += flags_len

        assert offset == len(response)

        return app_name, version
    except ExceptionRAPDU as e:
        if e.status == 0x5515:
            raise ValueError("Your device is locked")
        raise e


def exit_current_app(backend):
    backend.exchange(
        cla=0xB0,  # specific CLA for BOLOS
        ins=0xA7,  # specific INS for INS_APP_EXIT
        p1=0,
        p2=0)


def open_app_from_dashboard(backend, app_name: str):
    try:
        backend.exchange(
            cla=0xE0,  # specific CLA for Dashboard
            ins=0xD8,  # specific INS for INS_OPEN_APP
            p1=0,
            p2=0,
            data=app_name.encode())
    except ExceptionRAPDU as e:
        if e.status == 0x5501:
            raise ValueError("Open app consent denied by the user")
        elif e.status == 0x6807:
            raise ValueError(f"App '{app_name} is not present")
        raise e
