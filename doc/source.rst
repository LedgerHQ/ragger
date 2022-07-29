Code documentation
==================

Backend
-------

The contract a backend must respect:

.. autoclass:: ragger.backend.BackendInterface
    :members:

Responses
---------

Most APDU response are instances of class RAPDU:

.. autoclass:: ragger.RAPDU

However, if the backend has its raise_policy configured to raise on the
received APDU response, it will raises an `ExceptionRAPDU`:

.. autoclass:: ragger.ExceptionRAPDU

The different values of `RaisePolicy` are :

.. autoclass:: ragger.backend.RaisePolicy
