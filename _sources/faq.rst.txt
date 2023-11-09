Frequently Asked Questions
==========================

.. contents::
  :local:
  :backlinks: none

Installation / integration
--------------------------

Why all my tests are raising a ``ConnectionError`` when using SpeculosBackend?
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This indicates that :term:`Speculos` could not reach its server, generally
because the emulator could not be started.

With verbose options, you should be able to find in the logs the Speculos
command line, which should look like:

.. code-block:: bash

  /usr/bin/python3 -m speculos --model nanos --sdk 2.1 --display headless /<absolute_path>/<application_name>.elf

Try and launch this command line by itself to try and see the original error. It
could be that:

- the application ELF file does not exists
- the ``model`` or ``sdk`` version does not exists
- Speculos is already started elsewhere, and the network port are not available
- Speculos is not installed
- ``qemu-arm-static`` (used by Speculos under the hook) is not installed

...and if I'm getting a ``NotADirectoryError``?
+++++++++++++++++++++++++++++++++++++++++++++++

This is a rare case that can occur if the user's ``$PATH`` contains
dubiously-formed directories. (Re-)Installing ``qemu-arm-static`` (see
:ref:`here <Installation-Apt>`) seems to solve the issue.

Architecture / code
-------------------

Can I control how the backend behaves when receiving a response from the application?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Backends can be instantiated with a
:py:class:`RaisePolicy <ragger.backend.interface.RaisePolicy>`, which controls
how a backend should react when receiving a response from the
:term:`application` it is communicating with.

By default, this policy is ``RaisePolicy.RAISE_ALL_BUT_0x9000``, which means the
backend will raise an :py:class:`ExceptionRAPDU <ragger.error.ExceptionRAPDU>`
if the :term:`APDU` returned by the :term:`application` does not end with
``b'0x9000'``, else returns a :py:class:`RAPDU <ragger.utils.structs.RAPDU>`
instance. This behavior can be change with the three other options:

- ``RaisePolicy.RAISE_NOTHING``, where the backend will never raise, and always
  returns a proper :py:class:`RAPDU <ragger.utils.structs.RAPDU>`.
- ``RaisePolicy.RAISE_ALL``, where the backend will always raise a
  :py:class:`ExceptionAPDU <ragger.error.ExceptionRAPDU>`, whatever the status.
- ``RaisePolicy.RAISE_CUSTOM``, where the backend will raise a
  :py:class:`ExceptionAPDU <ragger.error.ExceptionRAPDU>`, for :term:`APDU` ending with 
  status defined in ``whitelisted_status``.

From that, every higher-level error management can be performed on top of
``Ragger``.
