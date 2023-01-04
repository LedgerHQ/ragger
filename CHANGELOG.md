# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- conftest: `--log_apdu_file <filename>` option
- firmware: `Firmware:have_bagl` and `Firmware:have_nbgl` properties indicates which graphical
            interface the firmware implements.

### Fixed


## [1.1.0] - 2023-01-02

### Added

- Fatstacks UseCaseHomeExt
- navigator: Improve navigation by waiting screen changes instead of hardcoded sleeps
- navigator: navigate_and_compare(): Add optional snap_start_idx parameter
- navigator: navigate_until_text(): take a list of validation instructions and check last screen


## [1.0.0] - 2022-12-26

### Added

- Initial version
