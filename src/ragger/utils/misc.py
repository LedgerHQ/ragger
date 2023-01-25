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
