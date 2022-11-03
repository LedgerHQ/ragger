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
from typing import Dict, Tuple

from ragger.backend import BackendInterface
from ragger.firmware import Firmware

LAYOUT_PREFIX = "layout_"


class MetaScreen(type):
    """
    Creates a class with a constructor automatically instanciating layouts
    from declared class attributes.

    The goal is to build a representation of a screen in a declarative way. Layouts must be declared
    as attributes of the class, their name starting with the prefix `layout_`. These attributes will
    then be instantiated and stored in the class instance, without their `layout_` prefix.

    For instance, let's imagine an application with an information button header, a cancel/quit
    footer and a keyboard in the center of the screen. The declaration of such screen would be:

    ```python
    class Screen(metaclass=MetaScreen):
        layout_header = InfoHeader
        layout_keyboard = LetterOnlyKeyboard
        layout_footer = CancelFooter
    ```

    When instantiated, the class `Screen` will also instantiate `InfoHeader`, `LetterOnlyKeyboard`
    and `CancelFooter`, and store them as instance attributes (after removing the `layout_` prefix).
    They could then be used immediately:


    ```python
    screen = Screen(client, firmware)

    screen.header.tap()             # entering the 'info' view
    screen.footer.tap()             # going out the 'info' view
    screen.keyboard.write("hello")  # writting 'hello' on the keyboard
    screen.footer.tap()             # going out the 'app' view
    try:
        screen.footer.tap()         # quitting the application
    except:
        pass                        # depending on the backend, the application stop could raise
                                    # an error
    ```

    (Of course the navigation depends on the current application, so this example may not work in
    most cases).

    """

    def __new__(cls, name: str, parents: Tuple, namespace: Dict):
        layouts = {
            key.split(LAYOUT_PREFIX)[1]: namespace.pop(key)
            for key in list(namespace.keys()) if key.startswith(LAYOUT_PREFIX)
        }

        def init(self, client: BackendInterface, firmware: Firmware):
            for attribute, cls in layouts.items():
                setattr(self, attribute, cls(client, firmware))

        namespace["__init__"] = init
        return super().__new__(cls, name, parents, namespace)
