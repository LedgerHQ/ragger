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
from functools import partial
from pathlib import Path
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QWidget, QDesktopWidget, \
    QMainWindow, QAction, qApp, QLabel, QPushButton, QSizePolicy, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap, QFont
from typing import Callable

from ragger.logger import get_gui_logger

BUTTON_HEIGHT = 50

# Fatstacks has the bigger screen, so everything is scaled around it
SCREENSHOT_MAX_WIDTH = 400
SCREENSHOT_MAX_HEIGHT = 670
BORDER = 50

WIDTH = SCREENSHOT_MAX_WIDTH + BORDER * 2
HEIGHT = SCREENSHOT_MAX_HEIGHT + BUTTON_HEIGHT + BORDER * 2

INDEX = 4


class RaggerMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.logger = get_gui_logger().getChild("QWindow")
        self._init_UI()
        self.logger.info("Initiated")

    def _init_UI(self):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Menu')
        fileMenu.addAction(exitAct)
        self.resize(WIDTH, HEIGHT)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Ragger - Ledger Nano app automation framework')
        self.setWindowIcon(QIcon('/home/lpascal/repos/tools/ragger/doc/images/ragger.png'))
        self._central_widget = QWidget(self)
        self._central_widget.setObjectName("central_widget")
        self._init_central_screenshot()
        self.show()

    def _bigger(self, screenshot: Path) -> QPixmap:
        return QPixmap(str(screenshot.resolve()))\
            .scaled(SCREENSHOT_MAX_WIDTH, SCREENSHOT_MAX_HEIGHT, Qt.KeepAspectRatio)

    def _init_screenshot(self) -> None:
        self._screenshot = QLabel(self._central_widget)
        self._screenshot.setGeometry(QRect(0, 0, SCREENSHOT_MAX_WIDTH, SCREENSHOT_MAX_HEIGHT))
        self._screenshot.setScaledContents(False)
        self._screenshot.setObjectName("screenshot")
        self._screenshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._screenshot.setAlignment(Qt.AlignCenter)
        self._screenshot.setStyleSheet("QLabel {background-color: gray;}")

    def _init_validation_buttons(self) -> None:
        self._yes = QPushButton(self._central_widget)
        self._yes.setGeometry(QRect(0, SCREENSHOT_MAX_HEIGHT, WIDTH // 2, BUTTON_HEIGHT))
        self._yes.setObjectName("valid_button")
        self._no = QPushButton(self._central_widget)
        self._no.setGeometry(QRect(WIDTH // 2, SCREENSHOT_MAX_HEIGHT, WIDTH // 2, BUTTON_HEIGHT))
        self._no.setObjectName("invalid_button")

    def _init_central_screenshot(self) -> None:
        self._init_screenshot()
        self._init_validation_buttons()
        layout = QGridLayout()
        layout.addWidget(self._screenshot, 0, 0)
        layout.addWidget(self._yes, 1, 0)
        layout.addWidget(self._no, 2, 0)
        self._central_widget.setLayout(layout)
        self.setCentralWidget(self._central_widget)

    def close(self) -> None:
        """
        Stop the Qt application
        """
        self.logger.info("Closing")
        qApp.quit()

    def set_button_cb(self, callback: Callable[[bool], None]) -> None:
        """
        Set the callback to be called when the user clicks on the "Yes/Confirm/Continue" or
        "No/Cancel/Stop" buttons. This callback shall receive one boolean argument, which will
        be `True` if the clicked button is "Yes", and `False` otherwise.

        :param callback: The callback to set on the button
        :type callback: Callable[[bool], None]
        """
        self.logger.debug("New callback received")
        self._yes.clicked.connect(partial(callback, True))
        self._no.clicked.connect(partial(callback, False))

    def display_screenshot(self, image: Path) -> None:
        """
        Display an image in the center window of the interface.

        :param image: The path to the image to display
        :type image: Path
        """
        self.logger.debug("Displaying new screenshot '%s'", image)
        self._screenshot.setPixmap(self._bigger(image))
        self._yes.setText("YES, this is the correct screen")
        self._no.setText("NOPE, there is an error here")

    def display_action(self, action: str) -> None:
        """
        Display a text in the center window of the interface

        :param action: The text to display
        :type action: str
        """
        self.logger.debug("Displaying new action '%s'", action)
        custom_font = QFont()
        custom_font.setWeight(30)
        self._screenshot.setText(f"Please click on the {action}")
        self._screenshot.setFont(custom_font)
        self._yes.setText("Okay, I've performed the action")
        self._no.setText("Cancel the process")
