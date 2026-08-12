# Changelog

All notable user-facing changes are documented here.

## [Unreleased]

### Added

- Incremental per-chat cursors committed atomically with generated digests.
- Message-ID source citations and bounded, complete-message prompt chunks.
- Explicit protection against accidental remote exposure of the history viewer.

### Changed

- Added configuration validation before external services are contacted.
- Documented per-operator credential ownership and message-processing limits.
- Added automated tests, linting, build checks, and contribution/security guides.
- Run Telegram and webhook delivery inside the active async event loop.
- Expand coverage for configuration, delivery, fetching, storage, and digest cycles.
- Use the dependency lock and installed-wheel smoke test in CI.
