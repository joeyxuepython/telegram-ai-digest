# Codex for Open Source application notes

Use this document as an evidence checklist when completing the application. It
does not assert usage or community metrics that the repository has not earned.

## Project summary

Telegram AI Digest is an MIT-licensed, local-first tool for producing structured
summaries of authorized Telegram chats. It combines Telethon, a user-provided
OpenAI API key, local SQLite storage, and optional local web history browsing.

## Evidence to link

- Public repository: `https://github.com/joeyxuepython/telegram-ai-digest`
- License: [MIT](../LICENSE)
- Security and credential boundary: [SECURITY.md](../SECURITY.md) and
  [PRIVACY.md](../PRIVACY.md)
- Contribution process: [CONTRIBUTING.md](../CONTRIBUTING.md)
- Automated checks: `.github/workflows/ci.yml`

## Verifiable engineering evidence

- Incremental per-chat cursors are committed atomically with generated digests.
- Failed or oversized chat batches do not advance cursors, preventing silent data loss.
- Telegram and webhook delivery run inside one async event loop.
- Telegram text is treated as untrusted prompt input and important claims are
  requested with source message IDs.
- Large chat windows are split into bounded, complete-message chunks.
- The local web viewer escapes stored content and rejects remote binding unless
  the operator explicitly opts in.
- CI tests Python 3.10, 3.11, and 3.12 from the committed lock file, builds the
  package, and smoke-tests the installed wheel.

## Honest maintainer statement

State the maintainer role, the user problem being solved, and concrete evidence
of adoption only when it is available (for example, release history, issue
activity, downstream users, or download metrics). Do not claim that OpenAI
sponsors, endorses, or uses this project. Do not claim a number of users,
downloads, or stars without a dated source.

## Before submitting

- Ensure the default branch CI is green.
- Create a reviewed release tag when a stable version is ready.
- Remove any credentials, session data, or real chat content from git history.
- Describe the project's current maturity accurately; a new project can apply,
  but selection is decided by the program maintainers.

## Evidence that code cannot manufacture

Do not submit until the application can cite at least one genuine adoption
signal: an external user deployment, package downloads, an independently filed
issue, an external pull request, or a documented community use case. Record the
date and public source for every number. Never create artificial stars,
downloads, users, or contributor activity.

## Appropriate use of maintainer API credits

If requested, describe credits for OSS maintenance rather than subsidizing end
user summaries: issue triage, focused test generation, pull-request review,
security analysis, release notes, and keeping English and Chinese documentation
consistent.
