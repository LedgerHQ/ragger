Code documentation
==================

.. contents::
  :local:
  :backlinks: none


``ragger.backend``
------------------

``ragger.backend.interface``
++++++++++++++++++++++++++++

Interface contract
''''''''''''''''''

The contract a backend must respect:

.. autoclass:: ragger.backend.BackendInterface
   :members:

Response management policy
''''''''''''''''''''''''''

To change the behavior of the backend on :term:`response APDU <RAPDU>`, one can
tinker with the ``RaisePolicy``:

.. autoclass:: ragger.backend.interface.RaisePolicy
   :members:
   :undoc-members:

Concrete backends
+++++++++++++++++

Speculos backend (emulator)
'''''''''''''''''''''''''''

.. autoclass:: ragger.backend.SpeculosBackend
   :members:

Physical backends
'''''''''''''''''

.. autoclass:: ragger.backend.LedgerCommBackend
   :members:

.. autoclass:: ragger.backend.LedgerWalletBackend
   :members:

``ragger.error``
----------------

.. autoclass:: ragger.error.ExceptionRAPDU


``ragger.firmware``
-------------------

``ragger.firmware.firmware``
++++++++++++++++++++++++++++

Most ``Ragger`` high-level class needs to know which :term:`Firmware` they
should expect. This is declared with this class:

.. autoclass:: ragger.firmware.Firmware
   :members:

``ragger.firmware.stax``
++++++++++++++++++++++++

``ragger.firmware.stax.screen``
'''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.stax.screen
   :members:

``ragger.firmware.stax.layouts``
'''''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.stax.layouts
   :members:
   :undoc-members:

``ragger.firmware.stax.use_cases``
''''''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.stax.use_cases
   :members:
   :undoc-members:

``ragger.firmware.version``
+++++++++++++++++++++++++++

VersionManager
''''''''''''''

Versions are managed through the ``VersionManager``

.. autoclass:: ragger.firmware.versions.VersionManager
   :members:


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

Managed SDK & versions
''''''''''''''''''''''

.. autodata:: ragger.firmware.versions.SDK_VERSIONS

``ragger.navigator``
--------------------

Interface and instructions
++++++++++++++++++++++++++

.. automodule:: ragger.navigator.navigator
   :members:
   :undoc-members:

``ragger.utils``
----------------

``ragger.utils.structs``
++++++++++++++++++++++++

.. autoclass:: ragger.utils.structs.RAPDU

``ragger.utils.misc``
+++++++++++++++++++++

.. autofunction:: ragger.utils.misc.app_path_from_app_name
