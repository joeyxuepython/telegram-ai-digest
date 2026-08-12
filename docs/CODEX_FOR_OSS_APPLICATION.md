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
