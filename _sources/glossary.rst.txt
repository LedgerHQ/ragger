.. _Glossary:

Glossary
========

.. glossary::

   APDU
     **APDU** stands for
     `Application Protocol Data Unit <https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit>`_.
     It designate a message which is transmitted from a :term:`client` to an
     :term:`application`, or the other way around. APDUs transit through USB or
     Bluetooth.

   Application
     In this documentation, an **application** is a piece of software, build
     around the Ledger Secure SDK, which runs on a Ledger cold wallet device,
     such as a NanoS, NanoS+ or NanoX.

   Backend
     In ``Ragger``, a **backend** is a library which allows to communicate with
     a Ledger cold wallet device, either a real one (like a physical
     NanoS/S+/X), or an emulated one (thanks to ``Speculos``).

   Client
     A client is any piece of software accessing a service made available by a
     server; but in this documentation, a **client** refers to a piece of code
     able to communicate with an :term:`application`.

     Typically, the client of an application programmatically enables the
     capabilities of its application: signing a payload, triggering a
     transaction, changing the configuration, ...

   Firmware
     A **firmware** usually designates the Ledger device *device type* and SDK
     *version*. Currently, *device types* are NanoS, NanoS+ and NanoX. The
     *version* depends on the type.

     ``Ragger`` stores this information in the
     :py:class:`Firmware <ragger.firmware.Firmware>` class.

     See also :term:`SDK`.

   Golden snapshot
     In ``Ragger``, **golden snapshots** are :term:`application` screen's
     snapshots which are considered as references. They are used when testing an
     application to check the application behaves as expected.

   Layout
     In the Stax SDK, a **Layout** refers to an element displayed on a
     Stax screen. Examples of Layouts can be a button, on a specific
     location, a keyboard, or just a centered text. This name is used in
     ``Ragger`` to designate the class allowing to interact with a displayed
     layout.

     Layouts are used to create :term:`Pages <Page>` and
     :term:`Use Cases <Use Case>`

   LedgerComm
     **LedgerComm** is the original open-source library allowing to communicate
     with a Ledger device. It is hosted
     `on GitHub <https://github.com/LedgerHQ/ledgercomm>`__.

   LedgerWallet
     **LedgerWallet** is the newer open-source library allowing to communicate
     with a Ledger device. It is hosted
     `on GitHub <https://github.com/LedgerHQ/ledgerctl/>`__

   Page
     In the Stax SDK, a **Page** refers to a specific displayed Stax
     screen.A welcome page, a setting page are example of Pages. This name is
     also  used in ``Ragger`` to designate the class allowing to interact with a
     displayed page.

     Pages are created from :term:`Layouts <Layout>` and are used to create
     :term:`Use Cases <Use Case>`

   Pytest
     `Pytest <https://docs.pytest.org/>`_ is a largely used, open-source Python
     testing tool. Its ``fixture`` mechanism works neatly with ``Ragger``.

   RAPDU
     "Response APDU", designates the response of an :term:`application`
     following an :term:`APDU` from the :term:`client` to the application.

   SDK
     The **SDK** is the open-source code allowing an application to be compiled
     for a Ledger cold wallet device. It is hosted on GitHub.
   .. previous sentence should be linked to a centralized SDK repo

   Speculos
     **Speculos** is an open-source Ledger device emulator, allowing easy and
     fast testing of an :term:`application`. It is hosted
     `on GitHub <https://github.com/ledgerhq/speculos>`__.

     It is composed of the emulator itself, and a HTTP client-server module
     allowing to easily control and communicate with said emulator.

   Use Case
     In the Stax SDK, a **Use Case** refers to a pre-designed :term"`Page`
     or group of Pages. For instance, the settings Use Case manages one or
     several :term:`Pages <Page>` in order to display and change the settings.
     This name is used in ``Ragger`` to designate the class allowing to interact
     with a Use Case.

     Use Cases are created from :term:`Pages <Page>` and sometimes
     :term:`Layouts <Layout>`
