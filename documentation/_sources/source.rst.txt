Code documentation
==================

Backend
-------

The contract a backend must respect:

.. autoclass:: ragger.interface.BackendInterface
    :members:

Responses
---------

Most APDU response are instances of class RAPDU:

.. autoclass:: ragger.interface.RAPDU

However, if the backend has been instantiated with `raises=True`, APDU responses
with a status different from `0x9000` will raises an `ApduException`:

.. autoclass:: ragger.ApduException
