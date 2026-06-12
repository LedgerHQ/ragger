.. _Coverage:

==========================
 Functional test coverage
==========================

``Ragger`` can measure the **C code coverage of the firmware** exercised by the
functional tests, through the ``--coverage`` option. This complements the unit
tests: it tells which lines of the application sources are actually reached when
running the :term:`Speculos`-based functional suite.

.. note::

   Coverage is only available on the :term:`Speculos` backend (the application
   runs as ARM code inside an emulator, which is what makes the measurement
   possible). The application must be built **with debug symbols**: a default
   build keeps them, a stripped/release build does not.


Usage
=====

.. code-block:: bash

   # whole suite, single device -> coverage.info (+ coverage_html/ if genhtml is installed)
   pytest --device flex --coverage

   # custom output path
   pytest --device flex --coverage --coverage_output cov.info

   # several devices -> one file per device: coverage-<device>.info
   pytest --device all --coverage

The options added by the plugin are:

- ``--coverage``: enable tracing and produce the lcov file(s) at the end of the
  session.
- ``--coverage_output`` (default ``coverage.info``): the output lcov path. With
  several devices, one file per device is written as ``<stem>-<device>.info``.
- ``--coverage_exclude``: exclude matching source paths (repo-relative) from the
  report, typically a vendored submodule. Repeatable, and each value may be a
  comma-separated list; a pattern matches a path, a leading directory of it, or
  an fnmatch glob. Example: ``--coverage_exclude my-vendored-submodule``.

An HTML report (``<stem>_html/``) is rendered next to each lcov file when
``genhtml`` (from the ``lcov`` package) is available; otherwise only the lcov
file is produced.

.. note::

   SDK/toolchain files (under ``/opt``, ``/usr`` ...) are already dropped
   automatically because only sources found under the project root are kept.
   ``--coverage_exclude`` is meant for sources that *are* in the repository but
   should not be reported, such as a vendored git submodule.


Why not gcov?
=============

The usual C coverage flow relies on **gcov**: the application is compiled with
``-fprofile-arcs -ftest-coverage``, which produces ``.gcno`` files (the
build-time call graph) ; at runtime ``libgcov`` writes ``.gcda`` files (the
execution counters) when the process exits.

That flow **cannot** work on a Ledger application:

- ``libgcov`` is not linked into the firmware,
- the application never performs a normal libc ``exit()`` under BOLOS/Speculos,

so **no** ``.gcda`` is ever produced. ``Ragger`` therefore does **not** use gcov
at all (the build is not instrumented). Instead, coverage is reconstructed at
the **emulator** level, and the gcov building blocks are replaced by equivalents
that are available without instrumentation:

.. list-table::
   :header-rows: 1

   * - gcov
     - Ragger's approach
   * - ``.gcno`` (build-time address → line map)
     - the **DWARF line table** (``.debug_line``), already present in the ELF
   * - ``.gcda`` (runtime counters)
     - the **QEMU** ``in_asm`` **trace** (which blocks actually ran)
   * - ``gcov`` merge
     - intersecting the executed address ranges with the line table


How it works
============

:term:`Speculos` runs the ARM application through ``qemu-arm-static``. The
coverage pipeline is:

#. **Tracing.** QEMU honours the ``QEMU_LOG=in_asm`` / ``QEMU_LOG_FILENAME``
   environment variables. With ``in_asm``, QEMU logs the guest assembly of every
   *translated* basic block. A block is translated the first time it is reached,
   so "translated" == "executed at least once" == line coverage. (``exec,nochain``
   would log every execution -- orders of magnitude bigger -- and is not needed.)
   Enabling this requires no change to Speculos or QEMU: Speculos spawns QEMU
   with ``Popen`` without an explicit ``env``, so the variables set in
   ``os.environ`` are inherited. One trace file per QEMU process is written
   (``cov-<pid>.log``): the backend is usually class-scoped, so several QEMU
   instances run during a session and each must write its own file.

#. **Rebasing.** Ledger applications are PIC: linked high (e.g. ``0xc0de0000``)
   but loaded and executed by Speculos at a fixed base (``0x40000000`` for every
   Cortex-M target). The executed block addresses are rebased back to link
   addresses.

#. **Mapping.** The rebased ranges are intersected with the DWARF line table of
   the ELF to determine which source lines were covered.

#. **Output.** A standard lcov ``.info`` tracefile is emitted (uploadable to
   Codecov, renderable with ``genhtml``). Source paths are made repo-relative by
   stripping the longest prefix that still resolves to a file under the project
   root, which drops toolchain/SDK files (``/opt``, ``/usr`` ...).

The implementation lives in :py:mod:`ragger.utils.coverage`; the wiring (option,
per-device trace directory, end-of-session conversion) is in the ``Ragger``
``conftest`` and the :py:class:`SpeculosBackend
<ragger.backend.SpeculosBackend>`.


Limitations
===========

- **Line/block coverage only -- no branch coverage.** We only know that a block
  ran, not which side of a conditional was taken. Each covered line is reported
  with a hit count of 1 (presence/absence, not an execution frequency).
- The application ELF must keep its ``.debug_*`` sections (``-g``).
- Attribution is done on the optimized build (``-Os``), so the line mapping is as
  approximate as for any optimized-build coverage (inlining, shared lines).
