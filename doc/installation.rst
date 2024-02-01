.. _Installation:

Installation
============

``Ragger`` is currently available in the test ``pypi`` repository. It can be
installed with ``pip``:

.. code-block:: bash

   pip install ragger


By default - to avoid wasting useless time and space - the ``ragger`` package
comes with no :term:`backend`. Specific backend can be installed with extras:
``ragger[speculos]``, ``ragger[ledgercomm]``, ``ragger[ledgerwallet]``.
All backends can be installed with ``ragger[all_backends]``.


.. _Installation-Apt:

.. note::

   ``Speculos`` uses the ``qemu-arm-static`` executable under the hood, so
   you will need to install a system package for this. On Debian-based system,
   this executable lies in the ``qemu-user-static`` package, which can be
   installed it with:

   .. code-block:: bash

      sudo apt-get update && sudo apt-get install qemu-user-static
