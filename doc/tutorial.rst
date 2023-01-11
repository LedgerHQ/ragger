.. _Tutorial:

Tutorial
========

In this tutorial, we are going to develop glue code to leverage the capabilities
of ``Ragger`` in order to write tests which are able to run either on
:term:`Speculos` or on a physical device.

.. contents::
  :local:
  :backlinks: none

``Ragger`` installation
-----------------------

First step of all is the installation of ``Ragger``. At first, we are going to
test it with :term:`Speculos`, so we are going to install ``Ragger`` with Speculos
dependencies:

.. code-block:: bash

   $ pip install --extra-index-url https://test.pypi.org/simple/ ragger[speculos]

Some explanation on arguments:

- ``--extra-index-url https://test.pypi.org/simple/`` is necessary to get the
  latest version of ``Ragger``, as it is currently not deployed on the
  stable ``pypi`` repositories.
- ``ragger[speculos]`` means than Speculos and its dependencies will also
  be installed. ``Ragger`` tries to uncouple its dependencies so that only
  what is needed is installed.
  All the extras can be seen
  `in the setup.cfg <https://github.com/LedgerHQ/ragger/blob/develop/setup.cfg#L36-L100>`_
  file.

First backend instantiation
---------------------------

The ``SpeculosBackend``
+++++++++++++++++++++++

The :py:class:`BackendInterface <ragger.backend.BackendInterface>` really only
needs a :py:class:`Firmware <ragger.firmware.Firmware>` - declaring the type of
Ledger cold wallet to run the :term:`application` on, and the version of the
given :term:`SDK`, to be instantiated.

.. code-block:: python
  :linenos:

  from ragger.firmware import Firmware
  from ragger.backend import BackendInterface

  backend = BackendInterface(Firmware("nanos", "2.1.0"))  # this won't work, as it is an abstract interface

However, as we us Speculos which is going to start the :term:`application` inside an emulator,
we need to provide the application ELF file as an argument:

.. code-block:: python
  :linenos:

  from ragger.firmware import Firmware
  from ragger.backend import SpeculosBackend

  APPLICATION_ELF = "path/to/app.elf"

  backend = SpeculosBackend(APPLICATION_ELF, Firmware("nanos", "2.1.0"))

And that's it, you have a working backend! Although in the case of Speculos,
the emulator won't start immediately. You need to use a ``with`` statement
to start it and begin to exchange APDUs or other events with you application.

.. code-block:: python
  :linenos:

  with backend:
      backend.exchange(cla=0xE0, ins=0x01, data=bytes.fromhex("DEADBEEF"))
      backend.right_click()

This syntax will ensure that the backends properly clean what needs cleaning
once the communication is done. For Speculos, this mean stopping the whole
emulator, for other backend it could be as simple as closing a socket.

Backend as a fixture
++++++++++++++++++++

From this, we are not far away from writing a :term:`Pytest` fixture, wich could
take place in a ``conftest.py`` file, and used in a ``test_something.py`` file:

.. code-block:: python
  :caption: conftest.py
  :linenos:

  from pytest import fixture
  from ragger.firmware import Firmware
  from ragger.backend import SpeculosBackend

  APPLICATION_ELF = "path/to/application.elf"

  @fixture
  def backend() -> SpeculosBackend:
      backend = SpeculosBackend(APPLICATION_ELF, Firmware("nanos", "2.1.0"))
      with backend:
          yield backend

.. code-block:: python
  :caption: test_something.py
  :linenos:

  def test_something(backend):
      backend.exchange(cla=0xE0, ins=0x01, data=bytes.fromhex("DEADBEEF"))
      backend.right_click()

This code can then be trigger with ``Pytest`` like this:

.. code-block:: bash

  $ pytest -v test_something.py

  =============================== test session starts ===============================
  collected 1 item

  test_something.py::test_something PASSED                                     [100%]

  ================================ 1 passed in 0.41s ================================

Generalization
--------------

To other firmwares
++++++++++++++++++

When testing an application, it sounds logical to test not only a specific
:term:`Firmware`, but all supported ones. The common practice is to test
on the latest version of all Firmware (NanoS, NanoS+, NanoX). So we can declare
a list of those:

.. code-block:: python
  :linenos:

  from ragger.firmware import Firmware

  FIRMWARES = [Firmware('nanos', '2.1'),
               Firmware('nanox', '2.0.2'),
               Firmware('nanosp', '1.0.3')]


Then we can override the
`pytest_generate_tests <https://docs.pytest.org/en/7.2.x/how-to/parametrize.html#pytest-generate-tests>`_
function to automatically create a fixture (let's call it ``firmware``), which
will parametrize every test using this fixture and trigger then with each
declared firmware version:

.. code-block:: python
  :linenos:

  def pytest_generate_tests(metafunc):
  fw_list = list()
  ids = list()
      if "firmware" in metafunc.fixturenames:
          for fw in FIRMWARES:
              fw_list.append(fw)
              ids.append(fw.device + " " + fw.version)
          metafunc.parametrize("firmware", fw_list, ids=ids)

Now let's modify our previous ``backend`` fixture to use this ``firmware``
fixture:

.. code-block:: python
  :linenos:

  @fixture
  def backend(firmware) -> SpeculosBackend:
      backend = SpeculosBackend(APPLICATION_ELF, firmware)
      with backend:
          yield backend

Now this ``backend`` fixture is parametrized, and will trigger 3 times, with
successively ``firmware = Firmware('nanos', '2.1')``,
``firmware = Firmware('nanox', '2.0.2')`` and
``firmware = Firmware('nanosp', '1.0.3')``. The test will also be triggered 3
times, with each time a ``backend`` configured with a different application.

.. warning::
  The tests won't pass, because they may be started with every SDK versions,
  but the application ELF is not parametrized yet, and is still compiled for
  only one SDK type and version!

.. note::
  The application ELFs, hence the ELF file path has to be parametrized.

Thankfully, ``Ragger`` provides a
:py:func:`app_path_from_app_name <ragger.utils.misc.app_path_from_app_name>`
function which infers an application name ELF given its name and the firmware
name.

So, given you have a directory ``APPS_DIRECTORY`` where you stored all your
application ELFs, and they are all named as ``app_nanos.elf``,
``app_nanosp.elf``, ``app_nanox.elf``, this code will deduce their proper
name and location:

.. code-block:: python
  :caption: conftest.py
  :linenos:

  from pathlib import Path
  from pytest import fixture

  from ragger.firmware import Firmware
  from ragger.backend import SpeculosBackend
  from ragger.utils import app_path_from_app_name

  APPS_DIRECTORY = Path("path/to/")
  APP_NAME = "app"

  FIRMWARES = [Firmware('nanos', '2.1'),
               Firmware('nanox', '2.0.2'),
               Firmware('nanosp', '1.0.3')]

  def pytest_generate_tests(metafunc):
      fw_list = list()
      ids = list()
      if "firmware" in metafunc.fixturenames:
          for fw in FIRMWARES:
              fw_list.append(fw)
              ids.append(fw.device + " " + fw.version)
          metafunc.parametrize("firmware", fw_list, ids=ids)

  @fixture
  def backend(firmware) -> SpeculosBackend:
      app_location = app_path_from_app_name(APPS_DIRECTORY, APP_NAME, firmware.device)
      backend = SpeculosBackend(app_location, firmware)
      with backend:
          yield backend

And with this, all test should pass gracefully.

.. code-block:: bash

  $ pytest -v test_something

  =============================== test session starts ===============================
  collected 3 items

  test_something.py::test_something[nanos 2.1] PASSED                          [ 33%]
  test_something.py::test_something[nanox 2.0.2] PASSED                        [ 66%]
  test_something.py::test_something[nanosp 1.0.3] PASSED                       [100%]

  ================================ 3 passed in 1.90s ================================


To other backends
+++++++++++++++++

So far only Speculos was used as a backend. Let's see how to connect other ones.

Other backends are simpler the Speculos, because they do not manage the
application directly. Indeed, as Speculos embeds an emulator, the application
ELF file must be passed as an argument (and parametrized, ...).

Other backends do not need this. They assume the application is already up and
running somewhere, and will only try to connect on it when the time comes.

We need however the capability to decide which backend will be used when running
the test. Let's declare a ``Pytest`` ``--backend`` argument, and a fixture to
access it:

.. code-block:: python
  :linenos:

  def pytest_addoption(parser):
      parser.addoption("--backend", action="store", default="speculos")

  @fixture(scope="session")
  def backend_name(pytestconfig):
      return pytestconfig.getoption("backend")

Now that we are able to now wich backend is chosen, we can write a function
returning the correct backend:


.. code-block:: python
  :linenos:

  from ragger.backend import LedgerCommBackend, LedgerWalletBackend

  BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

  def create_backend(backend_name: str, firmware: Firmware, display: bool) -> BackendInterface:
      if backend.lower() == "ledgercomm":
          return LedgerCommBackend(firmware, interface="hid")
      elif backend.lower() == "ledgerwallet":
          return LedgerWalletBackend(firmware)
      elif backend.lower() == "speculos":
          args, kwargs = prepare_speculos_args(firmware, display)
          return SpeculosBackend(*args, firmware, **kwargs)
      else:
          raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")

Test can now be launched to run with another backend:

.. code-block:: bash

  $ # start the application on a physical device connected to the computer, or on an emulator
  $ pytest -v --backend ledgercomm test_something.py

.. warning::
  This won't work - again - because the tests will run for every SDK versions, but
  the application currently started could only be of one SDK version!

We can allow ``Pytest`` to specify the firmware by expanding/modifying our current code:

.. code-block:: python
  :caption: conftest.py
  :linenos:

  from pathlib import Path
  from pytest import fixture

  from ragger.firmware import Firmware
  from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend, BackendInterface
  from ragger.utils import app_path_from_app_name

  APPS_DIRECTORY = Path("path/to/")
  APP_NAME = "app"

  FIRMWARES = [Firmware('nanos', '2.1'),
               Firmware('nanox', '2.0.2'),
              Firmware('nanosp', '1.0.3')]

  BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

  def pytest_addoption(parser):
      parser.addoption("--backend", action="store", default="speculos")
      for fw in FIRMWARES:
          parser.addoption("--"+fw.device, action="store_true", help=f"run on {fw.device} only")

  @fixture(scope="session")
  def backend_name(pytestconfig):
      return pytestconfig.getoption("backend")

  def create_backend(backend_name: str, firmware: Firmware, display: bool) -> BackendInterface:
      if backend.lower() == "ledgercomm":
          return LedgerCommBackend(firmware, interface="hid")
      elif backend.lower() == "ledgerwallet":
          return LedgerWalletBackend(firmware)
      elif backend.lower() == "speculos":
          args, kwargs = prepare_speculos_args(firmware, display)
          return SpeculosBackend(*args, firmware, **kwargs)
      else:
          raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")

  def pytest_generate_tests(metafunc):
      if "firmware" in metafunc.fixturenames:
          fw_list = []
          ids = []
          # First pass: enable only demanded firmwares
          for fw in FIRMWARES:
              if metafunc.config.getoption(fw.device):
                  fw_list.append(fw)
                  ids.append(fw.device + " " + fw.version)
          # Second pass if no specific firmware demanded: add them all
          if not fw_list:
              for fw in FIRMWARES:
                  fw_list.append(fw)
                  ids.append(fw.device + " " + fw.version)
          metafunc.parametrize("firmware", fw_list, ids=ids)

  @fixture
  def backend(firmware) -> SpeculosBackend:
      app_location = app_path_from_app_name(APPS_DIRECTORY, APP_NAME, firmware.device)
      backend = SpeculosBackend(app_location, firmware)
      with backend:
          yield backend

And now we can easily specify which firmware should be used:

.. code-block:: bash

  $ # start the application on a physical device connected to the computer, or on an emulator
  $ pytest -v --nanosp --backend ledgercomm test_something.py

  =============================== test session starts ===============================
  collected 1 items

  test_something.py::test_something[nanosp 1.0.3] PASSED                       [100%]

  ================================ 1 passed in 0.22s ================================

Abstracting the interactions
----------------------------

Interacting programmatically with an application tends to be a non-trivial
thing, as complex processes (like performing a complete transaction) have to be
implemented through low-level actions on the device: forging bytes payloads (the
:term:`APDUs <APDU>`), triggering the buttons or the screen at the right time,
in the right places, in the right order, managing several screens, ...

Stax
++++

Interacting with the Stax screen, in particular, can be bothersome. It is
hard to keep track of button positions, pages layouts and such.

For instance let's imagine you develop an application with a welcome screen
with the application icon in the center, a "quit" clickable button on the
top right and a "info" clickable button on the lower center.

If you click on the "quit" button, well the application shuts down.

If you click on the "info" button the screen shows some application infos, with
a clickable "return" button on the lower center, which brings back to the
previous, welcome screen.

.. thumbnail:: images/stax_welcome.png
   :group: stax_base_group
   :width: 30%

.. thumbnail:: images/stax_infos.png
   :group: stax_base_group
   :width: 30%

This layouts has three clickable buttons. Basic interaction with them would be
something like:

.. code-block:: python
   :linenos:

   # going into the "info" screen
   backend.touch_finger(197, 606)

   # going back into the "welcome" screen
   backend.touch_finger(197, 606)

   # quitting the application
   backend.touch_finger(342, 55)


This does not look very complicated. However, this is just obfuscated code.
Without extended comment, you can't ask someone to understand or remember what
this code does. This is a guaranteed path to hard to maintain code.

Moreover, these pixel positions are not guaranteed to last. If the SDK chooses
to change some button position, or if higher-level graphic objects (such as
``Pages`` or ``UseCase``) changes the position (nothing prevents them to move
the "quit" button to the top left), all this code becomes deprecated.


That's why ``Ragger`` mimics the Stax SDK graphics library and provides
:term:`Layout` and :term:`Use Case` (:term:`Page` will also come soon) classes
that keep track of every interactive screen elements and expose meaningful
method to interact with them.

Layouts
'''''''

``Ragger``'s :py:class:`Layouts <ragger.firmware.stax.layout._Layout>` and
:py:class:`UseCases <ragger.firmware.stax.use_case._UseCase>` allows to
quickly describe an application screens and its attached behavior in a purely
declarative way, thanks to the
:py:class:`MetaScreen <ragger.firmware.stax.screen.MetaScreen>` metaclass.
For instance, with the previously described application:

.. code-block:: python
   :linenos:


   from ragger.firmware.stax.screen import MetaScreen
   from ragger.firmware.stax.layouts import ExitFooter, ExitHeader, InfoFooter

   class RecoveryAppScreen(metaclass=MetaScreen)
       layout_quit = ExitHeader
       layout_go_to_info_page = InfoFooter
       layout_return_to_welcome_page = ExitFooter

The metaclass will automatically detect all variables starting with ``layout_``
and create related attributes when the ``RecoveryAppScreen`` will be
instantiated. This latter will need - like a lot of ``Ragger`` classes - a
:term:`backend` and a :term:`firmware` as arguments.

Once instantiated, the created screen can be interacted with in a more flexible
way than if positions were still necessary:

.. code-block:: python
   :linenos:

   # let's say we still have a ``backend`` and a ``firmware`` fixture
   screen = RecoveryAppScreen(backend, firmware)

   # the application starts on the "welcome" page, from here we can either quit
   # the application, or go to the "info" page

   # this method call will trigger a ``finger_touch`` with the positions related
   # to the "info" centered lower button
   screen.go_to_info_page.tap()

   # now the application is on the "info" screen, it can only go back to the
   # "welcome" page
   screen.return_to_welcome_page.tap()

   # now the application is back on the "welcome" screen. Let's quit
   screen.quit.tap()

   # the application is now stopped

.. note::

   You may have noticed that the two centered lower buttons (the welcome page
   "info" button and the info page "return" button) are exactly at the same
   ``(x, y)`` positions, so why bother declaring them twice?

   First of all, the buttons may be at the same place, but they don't carry the
   same purpose, and it is a good idea to reflect that on the code.

   Second, if in a future version the Stax design changes and one of these
   button moves somewhere else on the screen's footer, **the layouts will be
   updated accordingly** in ``Ragger``, and the ``InfoFooter`` or ``ExitFooter``
   will still be valid, hence all code using this class remains valid too.

   If these arguments does not convince you, ``Ragger`` provides purely
   positional Layouts, and you can use ``CenteredFooter`` in replacement of both
   of these Layouts.

Use cases
'''''''''

But this is not simple enough *yet*. The previously shown screens are very
common, so common in fact that the SDK provides dedicated
:term:`Use Cases <Use Case>` to simplify their creation.

In this case, there is two. In the SDK, they are named:

- ``nbgl_useCaseHome``, which displays the "welcome" page, while allowing to
  access an "info" or "settings" page.
- ``nbgl_useCaseSettings``, which displays an "info" or "settings" page. This
  Use Case is very convenient when dealing with multiple info or settings which
  need several pages to be displayed (hence needs navigation buttons).

``Ragger`` replicates these Use Cases, and provides more meaningful methods on
top of them. Using Use Cases is very similar to Layouts; they need to be
declared as attribute of a class using the :py:class:`MetaScreen` metaclass,
and start with ``use_case_``:

.. code-block:: python
   :linenos:

   from ragger.firmware.stax.screen import MetaScreen
   from ragger.firmware.stax.use_case import UseCaseHome, UseCaseSettings

   class RecoveryAppScreen(metaclass=MetaScreen)
       use_case_welcome = UseCaseHome
       use_case_info = UseCaseSettings

   # let's say we still have a ``backend`` and a ``firmware`` fixture
   screen = RecoveryAppScreen(backend, firmware)

   # the application starts on the "welcome" page, from here we can either quit
   # the application, or go to the "info" page

   # this method call will trigger a ``finger_touch`` with the positions related
   # to the "info" centered lower button
   screen.welcome.info()

   # now the application is on the "info" screen, it can only go back to the
   # "welcome" page.
   # if the info needed to be shown on several pages, this Use Case also
   # provides navigation methods, ``.next`` and ``.back``
   screen.info.exit()

   # now the application is back on the "welcome" screen. Let's quit
   screen.welcome.quit()

   # the application is now stopped

The ``FullScreen`` class
''''''''''''''''''''''''

All these classes helps you tailoring a fairly elegant and straight-forward
client with meaningful and easy to write screen controls. However if you don't
feel like crafting you own screen representation, ``Ragger`` comes with a
:py:class:`FullScreen <ragger.firmware.stax.screen.FullScreen>` class
which embeds every existing :term:`Layout` and :term:`Use Case`.

It can be used to quickly instantiate a screen which could work with any
application screen, however of course, all action on this class are not
guaranteed to trigger a desired reaction (or no reaction at all) on the
application screen, as declared button can be totally fictional.

.. code-block:: python
   :linenos:

   from ragger.firmware.stax.screen import FullScreen

   screen = FullScreen(backend, firmware)

   # these use case methods will work in our case
   screen.home.info()
   screen.settings.exit()
   screen.welcome.quit()

   # layouts are also available, on these method will work too
   screen.info_footer.tap()
   screen.exit_footer.tap()
   screen.exit_header.tap()

   # this, however, will just randomly click on the screen and may or may not
   # trigger totally unrelated reaction
   screen.letter_only_keyboard.write("hello world!")
