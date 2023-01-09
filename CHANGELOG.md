# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed
- template: conftest.py: Use session scope for firmware and backend fixtures
- template: conftest.py: Targeted device must be specified with new `--device` required option.

### Fixed
- requirements: Removed the dependancy on protobuf package


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
