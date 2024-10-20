# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 2024-10-20

### Added

- `debug.py` launch configuration in `.vscode/launch.json`

### Changed

- Update launch config types, "python" -> "debugpy", in `launch.json`

### Fixed

- Fix breaking Nelnet website structure change:
  - New div was added near the top of the page.
  - New divs added in overview containing overall regular monthly
    payment amount and unpaid accrued interest. These pieces of
    info are skipped for now.

## [0.2.4] - 2024-08-09

### Changed

- Update login endpoint. Nelnet changed it from
  https://secure.nelnet.com/account/login
  to
  https://nelnet.studentaid.gov/account/login

## [0.2.3] - 2024-06-08

### Added

- `--version` option to CLI.
- Dev scripts for database update 2.

### Fixed

- Fix bug introduced by new Nelnet webpage field "Regular Monthly Payment
  Amount". Add "regular_monthly_payment_amount" column to
  "payment_information" database table, which is one of the per-loan-
  group tables.

## [0.2.2] - 2024-06-07

### Fixed

- Fix bug with repayment_plan field due to Nelnet website update.
