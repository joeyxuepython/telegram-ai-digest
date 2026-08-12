"""AI summarizer — generate digest from fetched messages."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from openai import OpenAI

from .config import Config, get_config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant that creates structured summaries of Telegram group chat discussions.
Follow these rules:
1. Output in the user's requested language.
2. Group messages by topic, not chronologically.
3. For each topic: brief title, key points as bullets, mentioned links/tools.
4. Highlight: decisions made, important announcements, useful resources shared.
5. Keep the summary concise — focus on signal, ignore noise.
6. Format: Markdown.

Example output structure:
## 📋 {Group Name} — {Date} Digest

### 🔥 Hot Topics
- ...

### 📌 Key Decisions
- ...

### 🔗 Shared Resources
- ...

### 📊 Stats
- {N} messages from {M} participants
"""


def build_prompt(group_name: str, language: str, messages: list[dict]) -> str:
    """Build the user prompt for summarization."""
    lines = [f"Group: {group_name}\n"]
    for m in messages:
        time_str = m["date"].strftime("%H:%M") if isinstance(m["date"], datetime) else str(m["date"])
        lines.append(f"[{time_str}] {m['sender']}: {m['text']}")
    return "\n".join(lines)


def summarize(
    messages_by_chat: dict[int, list[dict]],
    cfg: Config | None = None,
) -> list[dict]:
    """Generate digests for each group's messages.

    Returns: [{"chat_id": int, "title": str, "content": str, "message_count": int, "participant_count": int}]
    """
    cfg = cfg or get_config()
    client = OpenAI(api_key=cfg.ai.api_key, base_url=cfg.ai.base_url or None)
    results: list[dict] = []

    for chat_id, msgs in messages_by_chat.items():
        if not msgs:
            continue
        try:
            participants = len({m["sender"] for m in msgs})
            prompt = build_prompt(
                f"Chat {chat_id}",
                cfg.output.language,
                msgs,
            )
            response = client.chat.completions.create(
                model=cfg.ai.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Language: {cfg.output.language}\n\n{prompt}"},
                ],
                max_tokens=cfg.ai.max_tokens,
                temperature=cfg.ai.temperature,
            )
            content = response.choices[0].message.content or ""
            results.append({
                "chat_id": chat_id,
                "title": f"Chat {chat_id}",
                "content": content,
                "message_count": len(msgs),
                "participant_count": participants,
                "generated_at": datetime.now(timezone.utc),
            })
            logger.info("Summarized %d messages from chat %s", len(msgs), chat_id)
        except Exception as exc:
            logger.error("Summarization failed for chat %s: %s", chat_id, exc)

    return results
