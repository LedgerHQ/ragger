# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.35.0] - 2025-05-14

### Changed

- Using `ledgered` Devices instead of local `Firmware` / `FIRMWARES`.
  Basically `ledgered.device.DeviceType` replaces the `ragger.firmware.Firmware` enum, and
  `ledgered.device.Devices` replaces `FIRMWARES`.
- `ragger.firmware.Firmware` is now a proxy to `ledgered` types and prints deprecation messages.

## [1.34.0] - 2025-04-28

### Changed

- Use pytest builtin --log-level instead of custom --Verbose

### Fixed

- Fix scenario navigation regular expression matching partial words

## [1.33.0] - 2025-04-23

### Added

- conftest: `--no-nav` option to completely disable the navigation during the tests.
- Retrieve `sdk_graphics` from elf file
- Add new functions `review_xxx_with_warning` to include the warning screen acknowledge
- Adapt `NavigationScenarioData` for Nano using NBGL

## [1.32.1] - 2025-04-04

### Fixed

- Reviews navigation on touchable devices (Flex, Stax) no longer 'taps', but 'swipes'

## [1.32.0] - 2025-03-31

### Changed

- Upgrade PyQt5 to PyQt6

## [1.31.1] - 2025-03-26

### Fixed

- Add missing method to physical device interface

## [1.31.0] - 2025-03-26

### Changed

- Reactivate logs like "Saving screenshot to image" (which were removed in v1.29.0)

## [1.30.0] - 2025-03-21

### Added

- Added support for Python 3.13

## [1.29.0] - 2025-03-06

### Changed

- Use `--Verbose` option to increase `pytest` verbosity. It adds log timestamps, some test-specific
  logs, and the verbose option is forwarded to Speculos.

## [1.28.0] - 2025-03-05

### Added

- Added --pki_prod option that can be forwarded to Speculos upon usage

## [1.27.1] - 2025-02-26

### Fixed

- Fixed backend being instantiated even when the test needs a different setup

## [1.27.0] - 2025-02-21

### Added

- Added support for different test setup

## [1.26.0] - 2025-02-06

### Added

- Added support for Python 3.12
- SWIPE support for physical backend

### Removed

- Drop support for Python 3.8

### Fixed

- `_actionhint` element location (covered previously by the snapshot image)
- Physical backend -specific imports (`PIL`, `tesseract`) are postponed to avoid raising when using
  Speculos only

## [1.25.0] - 2024-12-20

### Added
- navigator: `Navigator.navigate_until_text_and_compare` and `Navigator.navigate_until_text` now
             accept a `snap_start_idx` argument, like `Navigator.navigate_and_compare`.

## [1.24.0] - 2024-10-03

### Added
- conftest: Added 'all_eink' option for the `--device` argument to target Stax + Flex
- conftest: Added a autouse fixture to skip unsupported devices

### Fixed

- firmware/stax: Choice List positions were no longer correct compared to latest NBGL evolutions

## [1.23.0] - 2024-07-25

### Changed

- Rust app: get target directory from cargo metadata (workspace compatible)

## [1.22.1] - 2024-07-23

### Fixed

- firmware/flex: Wrong keyboard position

## [1.22.0] - 2024-07-22

### Added

- firmware/flex: Added the suggestion buttons positions (used with keyboard)

### Changed

- firmware/stax: Updated the suggestion buttons positions (used with keyboard)

### Fixed

- firmware/flex: Wrong keyboard position

## [1.21.1] - 2024-07-16

### Fixed
- Use SWIPE_CENTER_TO_LEFT in Stax navigation scenario

## [1.21.0] - 2024-07-12

### Added
- navigator: Now use Stax API_LEVEL_21 as layout for navigation

## [1.20.4] - 2024-07-11

### Fixed
- REVERT conftest: Fixed '--device all': limit the tests to devices declared in the App manifest

## [1.20.3] - 2024-07-11

### Fixed
- conftest: Fixed '--device all': limit the tests to devices declared in the App manifest

## [1.20.2] - 2024-07-02

### Fixed
- conftest: Fixed '--device all' conftest option

## [1.20.1] - 2024-06-19

### Fixed
- navigator: Moved review.tap coordinates on Stax from center to center left to avoid clicking on QR code button

## [1.20.0] - 2024-05-31

### Added
- conftest: Overridable fixture to inject custom arguments into the Speculos client

## [1.19.0] - 2024-05-14

### Added
- firmware/navigation: Adding swipe capabilities for Flex

### Changed
- navigation: scenarios now use `Firmware` enum rather than strings

## [1.18.2] - 2024-05-06

### Fixed
- backend: Adapting to new Speculos API `finger_touch` function.

## [1.18.1] - 2024-04-15

### Fixed
- navigator: fixed issue when using the custom_screen_text parameter

## [1.18.0] - 2024-04-12

### Added
- Flex firmware & navigation

### Changed
- firmware: 'stax' module is renamed 'touch', as it is no longer specific to the Stax device
- navigator: 'StaxNavigator' class is renamed 'TouchNavigator', as it is no longer specific to the
             Stax device

### Removed
- firmware: deprecated properties `Firmware.has_bal` and `has_nbgl`

## [1.17.0] - 2024-04-11

### Added
- Speculos backend: if not specified, availability of API and APDU ports are checked to avoid collision
- navigator: New pytest fixture to navigate by scenario to simplify classic navigation operations

### Fixed
- Speculos backend: Properly fixed internal snapshot state desync compare screen with text

## [1.16.3] - 2024-04-05

### Fixed
- Speculos backend: fixed internal snapshot state desync compare screen with text

## [1.16.2] - 2024-04-02

### Fixed
- backend: add missing tick_timeout argument from physical backends

## [1.16.1] - 2024-03-27

### Fixed
- firmware: stax: move `UseCaseSettings.previous` from `BUTTON_LOWER_MIDDLE` to `BUTTON_LOWER_LEFT`

## [1.16.0] - 2024-03-27

### Added:
- conftest: Integrating Rust application binary paths

### Changed
- conftest: `APP_DIR` and `LOAD_MAIN_APP_AS_LIBRARY` are replaced by the optional parameter
            `MAIN_APP_DIR`.
- firmware: stax: positions: Update settings exit for new SDK v15.2.0

## [1.15.0] - 2024-03-07

### Added
- navigator: `BaseNavInsID` allows to create custom `NavInsID` while using `Navigator` methods
             without additional type conversion.
- backend: Add optional argument to allow timeout in apdu exchange functions with default value of 5
           minutes

## [1.14.4] - 2024-02-21

### Fixed
- Fix search tree for main app binary in library mode

## [1.14.3] - 2024-02-09

### Changed
- Update search tree for main app binary in library mode

## [1.14.2] - 2024-01-31

### Fixed
- Removing the `frozen` attribute for `ExceptionRAPDU` dataclass, as Python3.11 `contextlib` needs
  the exception class it throws to be RW.

## [1.14.1] - 2024-01-19

### Fixed
- Update Ragger dependency versions (Speculos, LedgerComm, ledgerCTL), so that it can leverage recent
  features.

## [1.14.0] - 2024-01-19

### Added
- Batch generator with the `SpeculosBackend:batch` methods which allows to spawn several Speculos
  client of the same app, with (if needed) different seed, RNG and/or attestation or user keys.

## [1.13.1] - 2023-12-06

### Fixed
- SpeculosBackend: Removing `host` and `port` arguments, as they were modifying the client behavior,
  but not the server, so this feature probably never worked. The port can be changed through
  Speculos arguments: `args=["--api-port", "9876"]`.

## [1.13.0] - 2023-11-8

### Added
- interface: Adding RAISE_CUSTOM raise policy to allow custom definition of white-listed status.

## [1.12.0] - 2023-10-20

### Added:
- conftest: Add support for plugin testing

## [1.11.5] - 2023-09-27

### Changed:
- backend/speculos - navigator: Allow navigation screen content comparison with regex.

## [1.11.4] - 2023-07-31

### Changed:
- Requirements: Fail due to missing pytesseract only if really needed.

## [1.11.3] - 2023-07-31

### Changed:
- CI: Remove CI job dependency to allow deployment if wanted
- Dependency: Update needed Speculos version

## [1.11.2] - 2023-07-31

### Changed:
- firmware:use_case: Increase confirm time to 2.4 sec following SDK change

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

### Changed
- template: conftest.py: Target nanosp release 1.0.4 which is now supported by speculos
- backend: speculos.py: Do not pass `--sdk` argument anymore, this enforce using either last speculos supported SDK or app elf file with metadata.
- template: conftest.py/usage.md: Enable full Stax support
- Dependency: Use ledgerwallet>=0.2.3 to fix protobuff version issues
- Dependency: Use speculos>=0.1.202 to enable support for Last Stax firmware

### Fixed

- firmware/stax: Classes using `MetaScreen` can now declare their own `__init__` without it being overridden

## [1.3.1] - 2023-01-24

### Fixed

- backend/speculos : improved reliability of wait_for_screen_change
- firmware/stax : the "Suggestions" positions are shifted by Y+75px in order to fit with BOLOS
                  suggestion buttons, which are under the typing text area, not above.
- navigator: Don't clean already existing snapshots when running `navigate_and_compare()` through `navigate_until_text_and_compare()`.

## [1.3.0] - 2023-01-18

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
