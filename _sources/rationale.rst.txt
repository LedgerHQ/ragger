.. _Rationale:

===========
 Rationale
===========

Testing, easily manipulating a Ledger :term:`application` is hard. Although
:term:`Speculos` strongly eases it, it cannot always replace IRL tests on
physical devices.

There are libraries allowing to communicate with a physical device. However,
it would be very convenient to be able to develop code which would be compatible
wherever the application runs, either on an emulator or on a physical device.

On top of this, all these libraries provides low-level functions like pressing a
button or sending APDUs. Applications can be complex pieces of software and
testing one require higher-level code.

Abstracting the backends
========================

The original goal of ``Ragger`` is to make the manipulation of an
:term:`application` oblivious of the underlying device. Most applications are
tested against :term:`Speculos`, the Ledger device emulator, but it is not
always enough, and testing on real physical devices is often required.

``Ragger`` provides an interface which wraps several libraries:

- one emulator-only library: :term:`Speculos` (which uses itself as an emulator),
- two agnostic libraries, which can communicate with either a physical device,
  or an emulated one:

  - :term:`LedgerComm`
  - :term:`LedgerWallet`

In ``Ragger``, the classes embedding these libraries are called
:term:`backends<Backend>`. Any other backend can be added, given it respects the
:py:class:`BackendInterface <ragger.backend.BackendInterface>` interface.

.. thumbnail:: images/usage.svg
  :align: center
  :title: Software / communication layers between an application and its client
  :show_caption: true

Application :term:`clients<client>` using ``Ragger`` must comply with this
interface to communicate with the application. Once it's done, the client
can communicate with an application running either on top of an emulator or on
a real, physical device with very little cost.

Why not **no** cost? That's because the backend actually needs to talk to
something. Speculos is conveniently able to start its emulator itself, however
the other backends will need the application to be already started. Typically,
the application will have to be installed on a physical device, started, and the
device connected to the computer launching the client.

How to exploit these capabilities to write test running on both emulated or
physical device is documented in the :ref:`tutorial section<Tutorial>`.


Easing the development of application clients
=============================================

On top of abstracting the backend, ``Ragger`` provides tools and mechanisms
allowing to ease the development of application clients and write more thorough
tests.

.. _rationale_navigation:

Navigation
----------

In particular, ``Ragger`` offers abstraction layers to declare application flows
without repeating oneself. This is the role of the
:py:class:`Navigator <ragger.navigator.Navigator>` interface.

This class allows to declare a set of
:py:class:`navigation instructions <ragger.navigator.NavIns>`) which, bound with
callbacks, allows to abstract the expected behavior of an application.

Once the instructions are declared, it is possible to declare feature flows as
a list of instructions.

.. thumbnail:: images/navigate.svg
  :align: center
  :title: Software / communication layers between an application and its client
  :show_caption: true

The ``Navigator`` class also offers (with Speculos) screenshot checking
capabilities: while the instructions are performed, ``Ragger`` takes screenshots
of the application's screen, and is able to save them or compare them with
:term:`golden snapshots <golden snapshot>` to check if the application behaves
as expected.

This does not sound like much, but as soon as an application get a bit complex,
it helps a lot to write code which on the first hand manipulate high-level
concept as validating a transaction, and on the other hand deal with low-level
details such as crafting an :term:`APDU` and click on a button at the right time.

Touch screen management
-----------------------

Dealing with UI and user interaction is never simple. Nano devices has only two
user physical inputs, through the two buttons, which already allows some
elaborate combinations that could be challenging to test automatically.

With the touchable screens of Stax or Flex devices, the number of possibilities
drastically increases.

``Ragger`` embeds tools allowing to ease the development and the maintenance of
UI clients. this tools mainly consist of 3 components:

- the :py:class:`layout classes <ragger.firmware.touch.layouts>`, representing
  the layouts proposed in the NBGL section of the C SDK,
- the :py:class:`use cases classes <ragger.firmware.touch.use_cases>`,
  representing the use cases proposed in the NBGL section of the C SDK,
- the :py:mod:`screen module <ragger.firmware.touch.screen>`, allowing to nest
  the previous components in a single, centralized object.

.. note::

   If you are familiar with the :term:`NBGL` library, you will notice that
   ``Ragger`` does not implement a :term:`Page` representation. It will be
   integrated eventually.


These components bring multiple benefits:

- these abstractions prevent to directly use ``(X, Y)`` coordinates to interact
  with the screen and propose higher-level methods (for instance, when using the
  :py:class:`UseCaseHome <ragger.firmware.touch.use_cases.UseCaseHome>` use case,
  going to the settings is triggered with the method ``UseCaseHome.settings()``
  instead of touching the screen at ``(342, 55)``). The client's code is
  meaningful.
- ``Ragger`` internally keeps track of these positions on **every** :term:`SDK`
  version. If a new SDK version moves a button to other coordinates, the
  code written with the ``Ragger`` components will stay valid and functional.
- the :term:`layouts <Layout>` and :term:`use cases <Use Case>` mimic the
  :term:`NBGL` capabilities, so that the ``Ragger`` client screen architecture
  is close to the application one.
- the :py:class:`FullScreen <ragger.firmware.touch.screen.FullScreen>` class
  embeds every existing :py:class:`layout <ragger.firmware.touch.layouts>` and
  :py:class:`use case <ragger.firmware.touch.use_cases>` in a single class,
  providing a fast way of testing an interface without any other configuration.
- the :py:class:`MetaScreen <ragger.firmware.touch.screen.MetaScreen>` metaclass
  allows to build custom screen classes nesting the
  :py:class:`layouts <ragger.firmware.touch.layouts>` and the
  :py:class:`use cases <ragger.firmware.touch.use_cases>` of your choosing,
  creating a convenient and meaningful screen object where all UI interactions
  are centralized.


You can find example of these components in :ref:`this tutorial <tutorial_screen>`.
