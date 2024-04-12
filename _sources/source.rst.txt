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

Most ``Ragger`` high-level class needs to know which :term:`Firmware` they
should expect. This is declared with this class:

.. autoclass:: ragger.firmware.Firmware
   :members:
   :show-inheritance:

   .. autoattribute:: NANOS

   .. autoattribute:: NANOSP

   .. autoattribute:: NANOX

   .. autoattribute:: STAX

   .. autoattribute:: FLEX


``ragger.firmware.touch``
++++++++++++++++++++++++

``ragger.firmware.touch.screen``
'''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.touch.screen
   :members:

``ragger.firmware.touch.layouts``
'''''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.touch.layouts
   :members:
   :undoc-members:

``ragger.firmware.touch.use_cases``
''''''''''''''''''''''''''''''''''

.. automodule:: ragger.firmware.touch.use_cases
   :members:
   :undoc-members:

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
