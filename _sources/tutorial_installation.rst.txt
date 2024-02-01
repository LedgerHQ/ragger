``Ragger`` installation
=======================

First step of all is the installation of ``Ragger``. At first, we are going to
test it with :term:`Speculos`, so we are going to install ``Ragger`` with Speculos
dependencies:

.. code-block:: bash

   $ pip install ragger[speculos]

``ragger[speculos]`` means than Speculos and its dependencies will also be
installed. ``Ragger`` tries to uncouple its dependencies so that only what is
needed is installed. All the extras can be seen in the `setup.cfg
<https://github.com/LedgerHQ/ragger/blob/master/setup.cfg#L39-L74>`_ file.
