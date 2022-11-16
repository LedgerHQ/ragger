Frequently Asked Questions
==========================

Can I control how the backend behaves when receiving a response from the application?
-------------------------------------------------------------------------------------

Backends can be instantiated with a
:py:class:`RaisePolicy <ragger.backend.interface.RaisePolicy>`, which controls
how a backend should react when receiving a response from the
:term:`application` it is communicating with.

By default, this policy is ``RaisePolicy.RAISE_ALL_BUT_0x9000``, which means the
backend will raise an :py:class:`ExceptionRAPDU <ragger.error.ExceptionRAPDU>`
if the :term:`APDU` returned by the :term:`application` does not end with
``b'0x9000'``, else returns a :py:class:`RAPDU <ragger.utils.structs.RAPDU>`
instance. This behavior can be change with the two other options:

- ``RaisePolicy.RAISE_NOTHING``, where the backend will never raise, and always
  returns a proper :py:class:`RAPDU <ragger.utils.structs.RAPDU>`.
- ``RaisePolicy.RAISE_ALL``, where the backend will always raise a
  :py:class:`ExceptionAPDU <ragger.error.ExceptionRAPDU>`, whatever the status.

From that, every higher-level error management can be performed on top of
``Ragger``.
