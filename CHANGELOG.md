# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.11.1] - 2023-07-19

### Fixed:
- base conftest : hotfix option "all_nano"

## [1.11.0] - 2023-07-19

### Added:
- base conftest : add an "all_nano" option for the device parameter

## [1.10.2] - 2023-07-07

### Fixed
- physical backend gui : do not try to kill GUI process if it is not alive (causes error).

## [1.10.1] - 2023-07-03

### Fixed
- firmware: Adding a proxy `Firmware.device` property to ensure retro-compatibility with older
            `Firmware` usages. Previous change was breaking a lot of code.

## [1.10.0] - 2023-07-03

### Changed
- firmware: Removing the firmware version mechanism: as the device / version is embedded into each
            application ELF, Speculos alone can figure out how to emulate a device. Besides this,
            the version mechanism was only useful for the Stax graphical multi-version
            retrocompatibility, which is a niche usage not worth the complexity of the whole
            mechanism.
            Firmware is now an enum listing the currently supported devices (NanoS, NanoS+, NanoX
            and Stax).

## [1.9.2] - 2023-06-23

### Fixed
- navigator: Restore `NavInsID.USE_CASE_REVIEW_CONFIRM` custom wait for screen change for cases where the app call `io_seproxyhal_io_heartbeat()` before next screen is displayed.

## [1.9.1] - 2023-06-22

### Fixed
- speculos: Only pause ticker during navigation steps

## [1.9.0] - 2023-06-21

### Changed
- speculos: Default touch duration changed from 0.5sec to 0.1sec
- speculos: Control the ticker allowing to avoid any race issue when comparing screen and accessing OCR result
- speculos: Bump minimal speculos version to 0.2.5

## [1.8.2] - 2023-05-31

### Fixed
- import: Fix from 1.8.1 was not wide enough. Exception was filtered on 'QtCore', but they could
          also throw as 'QtWidgets'.

## [1.8.1] - 2023-05-31

### Fixed
- import: Feature developed in [this branch](https://github.com/LedgerHQ/ragger/pull/76) forced all
          Ragger installation to have PyQt5 and its dependencies installed. This is no longer the
          case.

## [1.8.0] - 2023-05-30

### Added
- backend: Physical backends (`LedgerComm`, `LedgerWallet`) can now pop a GUI in order to guide a
           user performing tests on a physical device.

### Changed
- package: Version is not longer hardcoded in sources, but inferred from tag then bundled into the
           package thanks to `setuptools_scm`

### Changed

### Fixed

## [1.7.3] - 2023-05-09

### Added
- configuration: Add a mechanism to specify the app dir where Speculos should search for the directory that holds the application compilation artifacts.

## [1.7.2] - 2023-05-05

### Added
- backend: StubBackend
- backend: Add a mechanism to survive USB stack reboot (`handle_usb_reset()`)
- backend: ledgerwallet/ledgercomm: Add a mechanism to check appname and open app at backend instantiation

### Fixed
- backend: Drop double logging of RAPDU on LedgerCommBackend and LedgerWalletBackend

## [1.7.1] - 2023-04-24

### Changed
- conftest: Set navigator fixture scope to backend one

## [1.7.0] - 2023-03-28

### Added
- backend: Add `wait_for_home_screen()`, `wait_for_text_on_screen()` and `wait_for_text_not_on_screen()`.
- navigator: Add `WAIT_FOR_SCREEN_CHANGE`, `WAIT_FOR_HOME_SCREEN`, `WAIT_FOR_TEXT_ON_SCREEN` and `WAIT_FOR_TEXT_NOT_ON_SCREEN` instructions.

### Changed
- backend: speculos: Based `wait_for_screen_change()` on screenshot comparison where it was previously based on OCR content.
- backend: speculos: Remove internal screen content reference update from `get_current_screen_content()`.
- navigator: Add a call to `wait_for_screen_change()` in `navigate()` similarly to what is done in `navigate_and_compare()`.
- navigator: Remove `USE_CASE_STATUS_WAIT` instruction, it should be replaced by `USE_CASE_STATUS_WAIT`.

### Fixed
- navigator: Sanitize the behavior of `USE_CASE_REVIEW_CONFIRM` navigation instruction.

## [1.6.0] - 2023-02-27

### Added
- navigator: Add USE_CASE_STATUS_DISMISS, this allows to dismiss the status instead of waiting for its end with USE_CASE_STATUS_WAIT.
- conftest: add configuration and pytest options that allow a custom seed to be used for speculos.

### Changed
- Dependency: Use speculos>=0.1.224 to avoid issues when running in slow setup.

### Fixed
 - backend: speculos.py: Strip empty text events from Speculos. This avoid false detection of screen change in navigation.

## [1.5.0] - 2023-02-17

### Added
 - conftest: new module that provides a base_conftest for unifying conftest features

### Changed
 - tests: the existing tests now use the new conftest module
 - CI: the CI now uses the reusable workflows for boilerplate compilation

### Fixed
 - tests: all tests are passing for Stax
 - misspelling fixes and new CI

## [1.4.0] - 2023-02-09

### Added

### Changed
- template: conftest.py: Target nanosp release 1.0.4 which is now supported by speculos
- backend: speculos.py: Do not pass `--sdk` argument anymore, this enforce using either last speculos supported SDK or app elf file with metadata.
- template: conftest.py/usage.md: Enable full Stax support
- Dependency: Use ledgerwallet>=0.2.3 to fix protobuff version issues
- Dependency: Use speculos>=0.1.202 to enable support for Last Stax firmware

### Fixed

- firmware/stax: Classes using `MetaScreen` can now declare their own `__init__` without it being overridden

## [1.3.1] - 2023-01-24

### Added

### Changed

### Fixed

- backend/speculos : improved reliability of wait_for_screen_change
- firmware/stax : the "Suggestions" positions are shifted by Y+75px in order to fit with BOLOS
                  suggestion buttons, which are under the typing text area, not above.
- navigator: Don't clean already existing snapshots when running `navigate_and_compare()` through `navigate_until_text_and_compare()`.

## [1.3.0] - 2023-01-18

### Added

### Changed
- template: conftest.py: Use session scope for firmware and backend fixtures
- template: conftest.py: Targeted device must be specified with new `--device` required option.
- unified naming of the Ledger Stax product: from `fat` or `fatstacks` to stax

### Fixed
- requirements: Removed the dependency on protobuf package


## [1.2.0] - 2023-01-04

### Added

- conftest: `--log_apdu_file <filename>` option
- firmware: `Firmware:have_bagl` and `Firmware:have_nbgl` properties indicates which graphical
            interface the firmware implements.
- navigator: Add USE_CASE_ADDRESS_CONFIRMATION_TAP
- navigator: `add_callback()` method to register callbacks after Navigator initialization

### Changed

- navigator: `NavIns` arguments of `navigate()` and higher-level methods can now also be `NavInsID`,
             which will automatically be converted to `NavIns` (with no argument for the callback)

### Fixed


## [1.1.0] - 2023-01-02

### Added

- Fatstacks `UseCaseHomeExt`
- navigator: Improve navigation by waiting screen changes instead of hardcoded sleeps
- navigator: `navigate_and_compare()`: add optional snap_start_idx parameter
- navigator: `navigate_until_text()`: take a list of validation instructions and check last screen


## [1.0.0] - 2022-12-26

### Added

- Initial version
