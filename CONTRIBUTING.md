# Contributing

Thanks for helping improve Telegram AI Digest.

## Before opening a pull request

1. Open an issue first for a substantial change so the scope can be discussed.
2. Keep credentials, Telegram session files, personal message data, and local
   databases out of commits and issue reports.
3. Add or update focused tests for behavior changes.
4. Run the local checks:

   ```bash
   python3 -m pip install -e ".[dev,web]"
   python3 -m pytest -q
   python3 -m ruff check .
   python3 -m ruff format --check .
   ```

## Pull request expectations

Explain the user-facing behavior, test evidence, and any privacy or security
impact. Avoid unrelated refactors. Maintainers may request changes before
merging.
