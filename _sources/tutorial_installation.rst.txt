``Ragger`` installation
=======================

First step of all is the installation of ``Ragger``. At first, we are going to
test it with :term:`Speculos`, so we are going to install ``Ragger`` with Speculos
dependencies:

.. code-block:: bash

   $ pip install --extra-index-url https://test.pypi.org/simple/ ragger[speculos]

Some explanation on arguments:

- ``--extra-index-url https://test.pypi.org/simple/`` is necessary to get the
  latest version of ``Ragger``, as it is currently not deployed on the
  stable ``pypi`` repositories.
- ``ragger[speculos]`` means than Speculos and its dependencies will also
  be installed. ``Ragger`` tries to uncouple its dependencies so that only
  what is needed is installed.
  All the extras can be seen
  `in the setup.cfg <https://github.com/LedgerHQ/ragger/blob/develop/setup.cfg#L36-L100>`_
  file.
