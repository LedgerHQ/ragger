Code documentation
==================

.. contents::
  :local:
  :backlinks: none


``ragger.backend``
------------------

The contract a backend must respect:

.. autoclass:: ragger.backend.BackendInterface
    :members:


Responses
+++++++++

Most APDU response are instances of class RAPDU:

.. autoclass:: ragger.RAPDU

However, if the backend has its raise_policy configured to raise on the
received APDU response, it will raises an `ExceptionRAPDU`:

.. autoclass:: ragger.ExceptionRAPDU

The different values of `RaisePolicy` are :

.. autoclass:: ragger.backend.RaisePolicy


``ragger.firmware``
-------------------

``ragger.firmware.firmware``
++++++++++++++++++++++++++++

Most ``Ragger`` high-level class needs to know which :term:`Firmware` they
should expect. This is declared with this class:

.. autoclass:: ragger.firmware.Firmware
   :members:

``ragger.firmware.version``
+++++++++++++++++++++++++++

Currently availabled version are these ones:

Nano S
''''''
.. autoclass:: ragger.firmware.versions.NanoSVersions
   :members:
   :undoc-members:

Nano S+
'''''''

.. autoclass:: ragger.firmware.versions.NanoSPVersions
   :members:
   :undoc-members:

Nano X
''''''

.. autoclass:: ragger.firmware.versions.NanoXVersions
   :members:
   :undoc-members:

VersionManager
''''''''''''''

Versions are managed through the ``VersionManager``

.. autoclass:: ragger.firmware.versions.VersionManager
   :members:
   :undoc-members:
