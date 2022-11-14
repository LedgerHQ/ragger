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

  from ragger.firmware import Firmware
  from ragger.backend import BackendInterface

  backend = BackendInterface(Firmware("nanos", "2.1.0"))  # this won't work, as it is an abstract interface

However, as we us Speculos which is going to start the :term:`application` inside an emulator,
we need to provide the application ELF file as an argument:

.. code-block:: python

  from ragger.firmware import Firmware
  from ragger.backend import SpeculosBackend

  APPLICATION_ELF = "path/to/app.elf"

  backend = SpeculosBackend(APPLICATION_ELF, Firmware("nanos", "2.1.0"))

And that's it, you have a working backend! Although in the case of Speculos,
the emulator won't start immediately. You need to use a ``with`` statement
to start it and begin to exchange APDUs or other events with you application.

.. code-block:: python

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

To other firmware
+++++++++++++++++

When testing an application, it sounds logical to test not only a specific
:term:`Firmware`, but all supported ones. The common practice is to test
on the latest version of all Firmware (NanoS, NanoS+, NanoX). So we can declare
a list of those:

.. code-block:: python

  from ragger.firmware import Firmware

  FIRMWARES = [Firmware('nanos', '2.1'),
               Firmware('nanox', '2.0.2'),
               Firmware('nanosp', '1.0.3')]


Then we can override the
`pytest_generate_tests <https://docs.pytest.org/en/7.2.x/how-to/parametrize.html#pytest-generate-tests>`_
function to automatically create a fixture (let's call it "firmware"), which
will parametrize every test using this fixture and trigger then with each
declared firmware version:

.. code-block:: python

  def pytest_generate_tests(metafunc):
  fw_list = list()
  ids = list()
      if "firmware" in metafunc.fixturenames:
          for fw in FIRMWARES:
              fw_list.append(fw)
              ids.append(fw.device + " " + fw.version)
          metafunc.parametrize("firmware", fw_list, ids=ids)

Now let's modify our previous ``backend`` fixture to use this firmware fixture:

.. code-block:: python

  @fixture
  def backend(firmware) -> SpeculosBackend:
      backend = SpeculosBackend(APPLICATION_ELF, firmware)
      with backend:
          yield backend

.. warning::
  This won't work, because the tests may be started with every SDK versions, but
  the application ELF is compiled for only one SDK!

.. note::
  The application ELFs, hence the ELF file path has to be parametrized too.

Thankfully, ``Ragger`` provides a `app_path_from_app_name` function which infers
an application name ELF given its name and the firmware name.

So, given you have a directory ``APPS_DIRECTORY`` where you stored all your
application ELFs, and they are all named as ``app_nanos.elf``,
``app_nanosp.elf``, ``app_nanox.elf``, this code will deduce their proper
name and location:

.. code-block:: python
  :caption: conftest.py

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

Other backend are simpler the Speculos, because they do not manage the
application directly. Indeed, as Speculos embeds an emulator, the application
ELF file must be passed as an argument (and parametrized, ...).

Other backends do not need this. They assume the application is already up and
running somewhere, and will only try to connect on it when the time comes.

We need however the capability to decide which backend will be used when running
the test. Let's declare a ``Pytest`` ``--backend`` argument, and a fixture to
access it:

.. code-block::

  def pytest_addoption(parser):
      parser.addoption("--backend", action="store", default="speculos")

  @fixture(scope="session")
  def backend_name(pytestconfig):
      return pytestconfig.getoption("backend")

Now that we are able to now wich backend is chosen, we can write a function
returning the correct backend:


.. code-block:: python

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
