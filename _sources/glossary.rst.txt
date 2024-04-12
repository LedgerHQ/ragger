.. _Glossary:

Glossary
========

.. glossary::

   APDU
     **APDU** stands for
     "`Application Protocol Data Unit <https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit>`_".
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

   BAGL
     **BAGL** stands for "BOLOS Application Graphics Library", and is a library
     integrated into the C SDK managing the UI of the NanoS, NanoX and NanoS+
     devices. It is embedded into the :term:`SDK`

   BOLOS
     **BOLOS** is `the operating system running on all Ledger hardware wallets
     <https://www.ledger.com/introducing-bolos-blockchain-open-ledger-operating-system>`_.
     Its code is not open-source. Its capabilities can be used through the
     open-source :term:`SDK`.

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
     application to check the application behaves as expected, by comparing them
     if actual snapshots.

   Layout
     In the :term:`Stax` SDK, a **Layout** refers to an element displayed on a
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

   NBGL
     **NBGL** stands for "New BOLOS Graphic Library", and is the successor of
     :term:`BAGL` for more recent devices such as :term:`Stax`. It is embedded
     into the :term:`SDK`.

     It has also been back-ported to older devices such as NanoS+ and NanoX (but
     not NanoS) to ease interface flow development.

   Page
     In the :term:`Stax` SDK, a **Page** refers to a specific displayed Stax
     screen.A welcome page, a setting page are example of Pages. This name is
     also  used in ``Ragger`` to designate the class allowing to interact with a
     displayed page.

     Pages are created from :term:`Layouts <Layout>` and are used to create
     :term:`Use Cases <Use Case>`

   Pytest
     `Pytest <https://docs.pytest.org/>`_ is a largely used, open-source Python
     testing tool. Its ``fixture`` mechanism is integrated into ``Ragger``.

   RAPDU
     "Response APDU" (**RAPDU**), designates the response of an
     :term:`application` following an :term:`APDU` from the :term:`client` to
     the application.

   SDK
     The **SDK** is the open-source code allowing an application to be compiled
     for a Ledger cold wallet device. On top of an interface to exploit
     :term:`BOLOS` capabilities, it provides boilerplate functions, graphic
     abstractions and other useful libraries for developing apps.

     It is written in C. Its code for the various devices has been unified into
     `this GitHub repository <https://github.com/LedgerHQ/ledger-secure-sdk>`_,
     although the current NanoS SDK is still based on an older version,
     versioned on `here <https://github.com/LedgerHQ/nanos-secure-sdk>`_.

     A Rust SDK also exists in
     `this repository <https://github.com/LedgerHQ/ledger-secure-sdk>`_,
     but should not yet be taken as production ready.



   .. previous sentence should be linked to a centralized SDK repo

   Speculos
     **Speculos** is an open-source Ledger device emulator, allowing easy and
     fast testing of an :term:`application`. It is hosted
     `on GitHub <https://github.com/ledgerhq/speculos>`__.

     It is composed of the emulator itself, and a HTTP client-server module
     allowing to easily control and communicate with said emulator.

   Stax
     **Stax** is the most premium Ledger device which, in a programmatic point
     of view, mostly differs from previous devices by its richer UI and a touch
     screen, justifying the usage of the new graphic library, :term:`NBGL`.

   Use Case
     In the :term:`Stax` SDK, a **Use Case** refers to a pre-designed
     :term:`Page` or group of Pages. For instance, the settings Use Case manages
     one or several :term:`Pages <Page>` in order to display and change the
     settings. This name is used in ``Ragger`` to designate the class allowing
     to interact with a Use Case.

     Use Cases are created from :term:`Pages <Page>` and sometimes
     :term:`Layouts <Layout>`
