# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

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
