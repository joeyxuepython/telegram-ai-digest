# Telegram AI Digest

[![CI](https://github.com/joeyxuepython/telegram-ai-digest/actions/workflows/ci.yml/badge.svg)](https://github.com/joeyxuepython/telegram-ai-digest/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Telegram AI Digest is a local-first command-line tool that turns messages from
Telegram groups you are authorized to access into structured Markdown digests.
It uses Telethon to retrieve messages and an OpenAI-compatible endpoint to
create the digest, then stores results in a local SQLite database.

The project does not include, collect, proxy, or share any user's Telegram or
OpenAI credentials. Every deployment uses credentials owned by its operator.

## What it does

- Fetches recent messages from configured Telegram chats.
- Generates one digest per chat, grouped by discussion topic.
- Sends digests to the terminal, Telegram Saved Messages, or a webhook.
- Stores local history and provides a small optional web viewer.

## Data and security boundary

Messages selected for summarization are sent to the OpenAI-compatible endpoint
configured by the operator. Only use the tool for chats where you have a lawful
and authorized basis to process and send messages to that provider. Review
[PRIVACY.md](PRIVACY.md) before deployment.

Never commit `config.yaml`, `.env*`, Telegram session files, SQLite databases,
or API keys. The repository ignores these paths by default.

## Quick start

Requires Python 3.10+ and a Telegram account/API application. The commands
below install from source; this project is not currently published to PyPI or
GHCR.

```bash
git clone https://github.com/joeyxuepython/telegram-ai-digest.git
cd telegram-ai-digest
python3 -m pip install -e ".[web]"
cp config.yaml.example config.yaml
```

Configure non-secret settings such as chat IDs in `config.yaml`, then provide
your own credentials in the shell that runs the service:

```bash
export TELEGRAM_API_ID="your_telegram_api_id"
export TELEGRAM_API_HASH="your_telegram_api_hash"
export OPENAI_API_KEY="your_openai_api_key"
export MONITOR_CHAT_IDS="-1001234567890,-1009876543210"
tad run
```

The first Telegram connection may ask for your account's login code. It creates
a local session under `data/`, which remains untracked.

### Commands

```bash
tad run --hours 24          # generate one digest per configured chat
tad watch --interval 60     # repeat every 60 minutes
tad history                 # view local digest history
tad web                     # start the local viewer on http://127.0.0.1:8080
```

### Docker (build from source)

```bash
docker build -t telegram-ai-digest .
docker run --rm \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -v "$(pwd)/data:/app/data" \
  -e TELEGRAM_API_ID -e TELEGRAM_API_HASH -e OPENAI_API_KEY -e MONITOR_CHAT_IDS \
  telegram-ai-digest tad run
```

## Development

```bash
python3 -m pip install -e ".[dev,web]"
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contributor workflow and
[SECURITY.md](SECURITY.md) for responsible vulnerability reporting. Community
expectations are in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Project status

The project is in its initial public release phase. It has automated tests and
continuous integration, but it does not claim production-scale adoption,
published package availability, or guaranteed summarization quality. Feedback,
reproducible bug reports, and contributions are welcome.

## License

Released under the [MIT License](LICENSE).
