Using and understanding the basis of ``Ragger`` testing capabilities
====================================================================

``Ragger`` is mostly used as a testing framework for Ledger application. To ease
the integration in such scenario, it includes pre-defined ``pytest`` fixtures
and pre-made configuration. This section shows how to use them.

.. note::

   On top of fixtures, options and other helpers brought by ``Ragger``, the
   tests written following this page guidance inherit every ``pytest`` base
   mechanisms, CLI arguments and so on. Refer to its
   `documentation <https://docs.pytest.org/en/latest/>`_ for further
   information.

.. contents::
   :local:
   :backlinks: none

Fast testing: using the embedded ``ragger.conftest`` module
-----------------------------------------------------------

Before creating any file, let's first create a directory dedicated to the tests.

.. code-block:: bash

  $ mkdir -p tests


``Ragger`` package contains a ``ragger.conftest`` module, including:

- a `base_conftest.py` module, defining ``pytest`` fixtures and CLI arguments,
- a `configuration.py` module, allowing to parametrize the previous fixtures.

As implied, ``Ragger`` relies on ``pytest`` to implement its testing
capabilities. Using these ``Ragger`` features hence requires a ``pytest`` setup.

In particular, ``pytest`` will fetch its configuration from a ``conftest.py``
file, so in this case one needs to create such a file, and import ``Ragger``
capabilities in it. A minimal ``conftest.py`` file would be:

.. code-block:: python
  :caption: tests/conftest.py
  :linenos:

  # This line includes the default `Ragger` configuration.
  # It can be modified to suit local needs
  from ragger.conftest import configuration

  # This line will be interpreted by `pytest` which will load the code from the
  # given modules, in this case `ragger.conftest.base_conftest`.
  # This module will define several fixtures, parametrized will the fields of
  # `configuration.OPTIONAL` variable.
  pytest_plugins = ("ragger.conftest.base_conftest", )

Now let's write a very basic test which does not do much, but will at least
allow to use our newly generated fixtures:

.. code-block:: python
  :caption: tests/test_first.py
  :linenos:

  # define the CLA of your application here
  CLA = 0xB0
  # define an instruction of your application here
  INS = 0x01

  def test_communicate(backend):
      print(backend.exchange(cla=CLA, ins=INS))


This test will use the :class:`backend <ragger.backend.BackendInterface>`
fixture in order to run the application into :term:`Speculos`. For that, we need
to access the application ELF file, which is expected to be stored in a specific
path. This path is in fact exactly where the default Ledger compilation
environment generates the ELF files, which is
``<git root directory>/build/<device name>/bin/app.elf``.

Let's say we are going to run the test on ``nanos`` only. The file system should
at least be like:

.. code-block:: bash

  $ tree .
  .
  ├── build
  │   └── nanos
  │       └── bin
  │           └── app.elf
  └── tests
      ├── conftest.py
      └── test_first.py

And now to run the tests:

.. code-block:: bash

  $ pytest --device nanos tests/ -v
  ========================================= test session starts ===========================================
  collected 1 item

  tests/test_first.py::test_communicate[nanos 2.1] PASSED                                            [100%]

  =========================================== 1 passed in 0.80s ===========================================


What happened?
++++++++++++++

This very simple setup actually triggered some interesting events:

- ``pytest`` automatically loaded the ``ragger.conftest.base_conftest`` module,
  and generated several fixtures to be used in following tests.
- one of these fixtures, ``backend`` is configured with several parameters. We
  did not specified it in the command line, but its type here is
  :class:`SpeculosBackend <ragger.backend.SpeculosBackend>` (the default
  type).

  This backend exchanges with an application running into the
  :term:`Speculos` emulator. For the fixture to automatically start this
  emulator, it needs to know what device it should emulates. That is where comes
  the ``--device nanos`` parameter.

  The fixture also needs to access the application ELF. That's why we have we
  stored it in ``build/nanos/bin/app.elf``.

  So when the ``backend`` fixture is created, it knows it needs to start a NanoS
  simulator in which the ``app.elf`` application file will be loaded.
- ``pytest`` finally discovers and runs the ``test_communicate`` test.

  The test receives the ``backend`` fixture, and uses it to exchange with the
  application running into the emulator. By default, the ``backend`` is
  configured to raise if the application replies with an error. In our case, the
  test passed, so the emulated application responded with a success status.

.. _tutorial_conftest_navigation:

A step forward: navigating into Nano applications
-------------------------------------------------

Now let's imagine we would like to test something with a bit of UI, for instance
going to the settings and coming back.

.. _tutorial_conftest scenario:

The scenario could be something like:

- the application start and displays a message (image ``00000.png``),
- a click on the right button brings the user to a screen with "settings"
  (image ``00001.png``),
- by clicking both buttons, the user enters the settings menu which displays
  some information (image ``00002.png``),
- by clicking the right button again, the screen now displays a cross - a way to
  go back to the home screen (image ``00003.png``),
- by clicking both buttons, the user goes back to the home screen (image
  ``00004.png``)

Although this scenario is very simple, we want to test it. How can it be done
with ``Ragger``?

That's where the :class:`navigator <ragger.navigator.navigator.Navigator>`
fixture comes into play.

Basic navigation example
++++++++++++++++++++++++

All the interactions described before can be implemented with this code:

.. code-block:: python
  :caption: tests/test_interface.py
  :linenos:

  from ragger.navigator import NavInsID

  def test_settings(navigator):
      instructions = [
          NavInsID.RIGHT_CLICK,
          NavInsID.BOTH_CLICK,
          NavInsID.RIGHT_CLICK,
          NavInsID.BOTH_CLICK
      ]
      navigator.navigate(instructions)

If you run this code with the ``--display`` CLI argument, you will see the
application UI being controlled by the test.

.. code-block:: bash

  $ pytest --device nanos --display tests/test_interface.py -v
  ======================================== test session starts ==========================================
  collected 1 item

  tests/test_first.py::test_settings[nanos 2.1] PASSED                                             [100%]

  ========================================== 1 passed in 0.80s ==========================================


More information on the navigator mechanism can be found in the :ref:`rationale
chapter <rationale_navigation>`.

Comparing snapshots
+++++++++++++++++++

Writing the test
''''''''''''''''

However nothing is tested yet. In order for the test to actually check that the
crossed screens are the expected ones, we need:

- to provide these expected snapshots (the :term:`golden snapshots
  <Golden snapshot>`)
- to use the method :meth:`navigator.navigate_and_compare
  <ragger.navigator.navigator.Navigator.navigate_and_compare>`.

  This method requires 3 mandatory arguments:

  - the ``path`` where the directory containing all the snapshot sets is
    located,
  - the ``test_case_name``, name of the snapshots test directory
  - the instruction list (just like with :meth:`navigator.navigate
    <ragger.navigator.navigator.Navigator.navigate>`

One nice thing with this method and ``Ragger`` ``conftest`` module is that these
snapshots can be automatically generated.

First, we have to modify our test file to use this method:

.. code-block:: python
  :caption: tests/test_interface.py
  :linenos:

  from pathlib import Path
  from ragger.navigator import NavInsID

  # this will point to the `tests/` directory
  TEST_DIRECTORY = Path(__file__).resolve().parent

  def test_settings(navigator):
      instructions = [
          NavInsID.RIGHT_CLICK,
          NavInsID.BOTH_CLICK,
          NavInsID.RIGHT_CLICK,
          NavInsID.BOTH_CLICK
      ]
      # navigator.navigate(instructions)
      navigator.navigate_and_compare(
          TEST_DIRECTORY,
          "settings",
          instructions,
          screen_change_before_first_instruction = False
      )


.. note::

   ``screen_change_before_first_instruction`` set to ``False`` means we are not
   expecting the application to change by itself, other than through our
   explicit inputs.

   The other way around can be the case, for example when testing the approval
   of a transaction: the test will first wait for a screen change (from the home
   screen to the transaction screen).

   Note that the ``screen_change_after_last_instruction`` argument also exists.
   We keep it to ``True`` in our case: we want to test that the last
   ``BOTH_CLICK`` instruction will bring us back to the home screen.

We can try and run this test, however, it will not work:

.. code-block:: bash

  $ pytest --device nanos tests/test_interface.py -v
  ============================================ test session starts =============================================
  collected 1 item

  tests/test_interface.py::test_settings[nanos 2.1] FAILED                                                [100%]

  ================================================== FAILURES ==================================================
  __________________________________________ test_settings[nanos 2.1] __________________________________________


                       [ STACK TRACE, STDOUT, STDERR AND OTHER CLASSIC PYTEST FAILURE INFO ]


  ========================================== short test summary info ===========================================
  FAILED tests/test_interface.py::test_settings[nanos 2.1] - ValueError: Golden snapshots directory
  (/tmp/lol/tests/snapshots/nanos/settings) does not exist.
  ============================================= 1 failed in 0.79s ==============================================

The interesting bit is the last message: ``Golden snapshots directory
(/absolute/path/tests/snapshots/nanos/settings) does not exist.``. Indeed we
wrote a test which will compare runtime snapshots with some reference ones, but
did not provided the latter.

Generating the golden snapshots
'''''''''''''''''''''''''''''''

So for this test to work, we need to have snapshots to compare to. These are not
always easy to produce, so ``Ragger`` provides a convenient way to produce
them automatically: the ``--golden_run`` CLI argument.

.. code-block:: bash

  $ pytest --device nanos tests/test_interface.py --golden_run -v
  ======================================== test session starts ==========================================
  collected 1 item

  tests/test_first.py::test_settings[nanos 2.1] PASSED                                             [100%]

  ========================================== 1 passed in 0.80s ==========================================

The test passed, without any snapshot provided? That's because this option
assumes you want to `register` snapshots rather than actually running the test.
So if we look at the file system now:

.. code-block:: bash

  $ tree .
  .
  ├── build
  │   └── nanos
  │       └── bin
  │           └── app.elf
  └── tests
      ├── conftest.py
      ├── snapshots
      │   └── nanos
      │       └── settings
      │           ├── 00000.png
      │           ├── 00001.png
      │           ├── 00002.png
      │           ├── 00003.png
      │           └── 00004.png
      ├── snapshots-tmp
      │   └── nanos
      │       └── settings
      │           ├── 00000.png
      │           ├── 00001.png
      │           ├── 00002.png
      │           ├── 00003.png
      │           └── 00004.png
      └── test_interface.py

You will notice two new repositories:

- a ``tests/snapshots`` directory has been created. This is due to the
  ``--golden_run`` argument, which registers all encountered screens into a
  dedicated test suite. As we used ``TEST_DIRECTORY`` (which is ``tests/``) as
  the snapshot root directory, it created a ``tests/snapshots`` directory.

  The tested device is a ``nanos`` here, so the test created a
  ``tests/snapshots/nanos`` directory.

  Finally, we named the test suite ``"settings"``, so the snapshots were stored
  into the ``tests/snapshots/nanos/settings`` directory.

- a ``tests/snapshots-tmp`` directory containing the same directories and files than
  the ``tests/snapshots`` directory. This is a directory which will always be created
  during a test run. ``Ragger`` will store the captured snapshot here, so that
  you will be able to compare them to the expected ones if a test were to fail.

  In our case, as the snapshots are captured in both time, the comparison always
  succeed.

  .. note::

    As this directory is created by ``Ragger`` during tests, it is advised to
    not version it, and rather to add ``snapshots-tmp`` into your ``.gitignore``
    file.

Assessing that the test is right
''''''''''''''''''''''''''''''''

At this point, you will need to check the snapshot images into the
``tests/snapshots/nanos/settings/`` directory. If they are what you were
expecting, then your test is good to go! You can now run it without the
``--golden_run`` argument, and version the tests and the snapshots so that you
will remain certain that further development modifying this behavior will not go
unnoticed.

.. code-block:: bash

  $ pytest --device nanos tests/test_interface.py -v
  ======================================== test session starts ==========================================
  collected 1 item

  tests/test_first.py::test_settings[nanos 2.1] PASSED                                             [100%]

  ========================================== 1 passed in 0.80s ==========================================


Out-of-the-box ``pytest`` ``Ragger`` tools
------------------------------------------

The previous tutorial explained some feature ``Ragger`` brings for application
testing. But there is more!

CLI parameters
++++++++++++++

``Ragger`` defines several parameters usable from the ``pytest`` CLI:


Controlling the backend (``--backend``)
'''''''''''''''''''''''''''''''''''''''

It is possible to change the backend on which the tests should run through a CLI
argument ``--backend``. Available backends are:

- ``--backend speculos``, using the :class:`SpeculosBackend
  <ragger.backend.SpeculosBackend>` (the default behavior),
- ``--backend ledgercomm``, using the :class:`LedgerCommBackend
  <ragger.backend.LedgerCommBackend>`,
- ``--backend ledgerwallet``, using the :class:`ledgerWalletBackend
  <ragger.backend.LedgerWalletBackend>`.

The two later options are physical backends, meaning they will try to connect to
the application through the USB ports. So the application should be installed on
a physical device, connected on the test computer through USB, and the
application being started on the device, else the tests will not run.

Controlling the devices (``--device``)
''''''''''''''''''''''''''''''''''''''

Running the tests on specific device is automatically integrated with the
``--device`` argument. Available devices are:

- ``--device nanos``,
- ``--device nanox``,
- ``--device nanosp``,
- ``--device stax``,
- ``--device all``.

This last option can only work with the :class:`SpeculosBackend
<ragger.backend.SpeculosBackend>` (as other backends rely on a physical device,
they can only run on the connected one), but is very convenient in a CI to
perform test campaign on all the devices.

Showing the device interface during test execution (``--display``)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. warning::

   Capability limited to the :class:`SpeculosBackend
   <ragger.backend.SpeculosBackend>`

With the :class:`SpeculosBackend <ragger.backend.SpeculosBackend>`, it is
possible to display the Qt graphical interface of the device, and so to follow
the actions and displayed screen during the test is executed.

This can be enabled with the ``--display`` CLI argument.

Controlling the seed (``--seed``)
'''''''''''''''''''''''''''''''''

.. warning::

   Capability limited to the :class:`SpeculosBackend
   <ragger.backend.SpeculosBackend>`

.. warning::

   Remember not to share your production seed. This option should be used only
   with testing, disposable seeds.


By default, the :class:`SpeculosBackend <ragger.backend.SpeculosBackend>` has
a fixed seed. It is possible to change its value with the ``--seed`` CLI argument.

Recording the screens (``--golden_run``)
''''''''''''''''''''''''''''''''''''''''

Some tests using high-level :class:`Navigator
<ragger.navigator.navigator.Navigator>` methods comparing snapshots can also
turn these methods into a "record mode": instead of comparing snapshots, they
will store the captured snapshots, with the ``--golden_run`` CLI argument.
This is convenient to automatically generate stock of :term:`golden snapshots
<Golden snapshot>`.

Recording the APDUs (``--log_apdu_file``)
'''''''''''''''''''''''''''''''''''''''''

It can be useful to record all the APDU transmitted between the client and the
application during a test. the ``--log_apdu_file`` allows to specify a file
path in which every :term:`APDU` and :term:`RAPDU` will be recorded.


Fixtures and decorators
+++++++++++++++++++++++

``Ragger`` defines several fixtures and decorators to customize how the tests runs
or access runtime information:

Running a test only on a specific backend
'''''''''''''''''''''''''''''''''''''''''

Some tests should only run on a specific backend. ``Ragger`` defines a
``pytest`` marker allowing to execute test only on the specified backend:

.. code-block:: python
  :caption: tests/test_first.py
  :linenos:

  import pytest

  CLA = 0xB0
  INS = 0x01

  # this will prevent this test from running,
  # except with the ``--backend ledgercomm`` argument
  @pytest.mark.use_on_backend("ledgercomm")
  def test_communicate(backend):
    print(backend.exchange(cla=CLA, ins=INS))

.. code-block:: bash

  $ pytest --device nanos --backend speculos tests/ -v

  ============================================ test session starts =============================================
  collected 1 item

  tests/test_first.py::test_communication[nanos 2.1] SKIPPED (skipped on this backend: "ledgercomm")      [100%]

  ============================================= 1 skipped in 0.81s =============================================


Getting the value of any CLI argument
'''''''''''''''''''''''''''''''''''''

Most argument defined by  ``Ragger`` into ``pytest`` can be reached through a
fixture, and used into any test:

- ``--backend`` is reachable with the ``backend_name`` fixture,
- ``--display`` is reachable with the ``display`` fixture,
- ``--golden_run`` is reachable with the ``golden_run`` fixture,
- ``--log_apdu_file`` is reachable with the ``log_apdu_file`` fixture,
- ``--seed`` is reachable with the ``backend_cli_user_seed`` fixture,

``--device`` is not immediately reachable through a fixture, but it can be found
with the ``backend`` fixture: ``backend.firmware.device``.
