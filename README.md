# 📋 Telegram AI Digest · [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/) [![CI](https://github.com/joeyxuepython/telegram-ai-digest/actions/workflows/ci.yml/badge.svg)](https://github.com/joeyxuepython/telegram-ai-digest/actions/workflows/ci.yml)

> 🇬🇧 English | [🇨🇳 中文](#telegram-ai-digest-中文)

**AI-powered daily/weekly digests for busy Telegram groups.** Connect, fetch, summarize — get a clean Markdown summary of what you missed. Built with Telethon + OpenAI.

## ✨ Why This Exists

You're in 20+ Telegram groups. You can't read everything. Telegram AI Digest fetches messages while you're away, runs them through GPT-4o-mini (cheap, fast), and delivers a structured summary — hot topics, key decisions, shared links — straight to your console, Saved Messages, or Slack.

```
$ tad run
⏳ Fetching messages from 3 groups...
🤖 Summarizing with OpenAI...
✅ Done!

📋 Chat -1001234567890 — 2025-08-12 Digest
━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Hot Topics
• Python 3.13 GIL removal discussion — 47 messages
• Best async ORM for production — 23 messages

📌 Key Decisions
• Team switching from SQLAlchemy to Prisma for new project

🔗 Shared Resources
• https://peps.python.org/pep-0703/
• https://github.com/tiangolo/fastapi/discussions/...

📊 142 messages from 28 participants
```

## 🚀 Quick Start

### 1. Install

```bash
pip install telegram-ai-digest
# Or from source:
git clone https://github.com/joeyxuepython/telegram-ai-digest.git
cd telegram-ai-digest
pip install -e .
```

### 2. Configure

```bash
cp config.yaml.example config.yaml
# Edit config.yaml:
#   - Add Telegram API ID + Hash (from https://my.telegram.org/apps)
#   - Add OpenAI API key (from https://platform.openai.com/api-keys)
#   - Add chat IDs to monitor
```

### 3. Run

```bash
# One-shot: fetch last 24h and generate digest
tad run

# Continuous: every 60 minutes
tad watch --interval 60

# View past digests
tad history

# Start web dashboard
tad web
# → http://localhost:8080
```

### Docker

```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml \
  -e OPENAI_API_KEY=sk-... \
  ghcr.io/joeyxuepython/telegram-ai-digest tad run
```

## 🧠 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Telethon     │────▶│  OpenAI API  │────▶│  Outputs      │
│  (fetch msgs) │     │  (summarize) │     │  console/     │
│               │     │              │     │  telegram/    │
│  SQLite ◀─────│─────│  Storage     │     │  webhook      │
└──────────────┘     └──────────────┘     └──────────────┘
```

- **Fetcher**: Pulls messages from configured groups via Telethon (async, efficient)
- **Summarizer**: Sends batched messages to OpenAI GPT-4o-mini (~$0.001 per digest)
- **Deliverer**: Routes output to console, Telegram Saved Messages, or webhook
- **Storage**: SQLite stores digest history for later browsing
- **Web**: FastAPI dashboard to browse past digests

## 📋 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_API_ID` | Telegram API ID | *(required)* |
| `TELEGRAM_API_HASH` | Telegram API hash | *(required)* |
| `OPENAI_API_KEY` | OpenAI API key | *(required)* |
| `MONITOR_CHAT_IDS` | Comma-separated chat IDs | *(required)* |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `DIGEST_MODE` | `hourly` / `daily` / `weekly` | `daily` |
| `DIGEST_LANGUAGE` | Output language | `zh` |

> ⚠️ Never commit `config.yaml` or `.env`. Use `.example` templates provided.

## 📊 Project

- **8 core modules** · ~800 lines of Python
- **Zero external DB required** — SQLite by default
- **pip installable** — single command setup
- **Async by design** — Telethon + asyncio

## 🤝 Contributing

PRs welcome! See issues for ideas. Run tests with:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## 📄 License

MIT — see [LICENSE](LICENSE).

---

# Telegram AI Digest [中文]

**AI 驱动的 Telegram 群聊摘要工具。** 自动拉取消息 → AI 生成摘要 → 推送到你面前。

## 为什么需要它

加入了 20+ 个技术群，根本看不过来。Telegram AI Digest 在你离线时自动拉取消息，用 GPT-4o-mini 生成结构化摘要（热点话题、关键决策、分享的链接），推送到终端、Saved Messages 或 Slack。

## 快速开始

```bash
pip install telegram-ai-digest
cp config.yaml.example config.yaml   # 填入 API 凭据
tad run                               # 一键生成摘要
tad watch --interval 60              # 每 60 分钟自动运行
tad web                               # 启动 Web 面板
```

## 架构

8 个模块，约 800 行 Python，默认 SQLite 零依赖部署，可通过 `pip install` 一键安装。

---

<p align="center">
  <sub>Built with ❤️ · <a href="https://github.com/joeyxuepython/telegram-ai-digest/issues">Issues</a> · <a href="https://github.com/joeyxuepython/telegram-ai-digest/discussions">Discussions</a></sub>
</p>
