"""Web dashboard — browse digest history."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse

from .config import get_config
from .storage import Storage

app = FastAPI(title="Telegram AI Digest", version="0.1.0")

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram AI Digest</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
        h1 { color: #2c3e50; }
        .digest { background: white; border-radius: 8px; padding: 20px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .meta { color: #7f8c8d; font-size: 0.85em; margin-bottom: 12px; }
        .content { line-height: 1.6; }
    </style>
</head>
<body>
    <h1>📋 Telegram AI Digest</h1>
    {% for d in digests %}
    <div class="digest">
        <div class="meta">
            Chat {{ d.chat_id }} · {{ d.message_count }} messages · {{ d.generated_at }}
        </div>
        <div class="content">{{ d.content | safe }}</div>
    </div>
    {% endfor %}
    {% if not digests %}
    <p>No digests yet. Run <code>tad run</code> to generate your first digest.</p>
    {% endif %}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index(chat_id: int | None = Query(None)):
    cfg = get_config()
    store = Storage(cfg.db_path)
    digests = store.list(chat_id=chat_id, limit=30)
    # Simple template rendering without jinja2 dependency
    rendered = TEMPLATE.replace("{{ d.chat_id }}", "{{ d.chat_id }}")
    for d in digests:
        d["content"] = d["content"].replace("\n", "<br>")
    # Use Python string formatting
    items = ""
    for d in digests:
        items += f"""<div class="digest">
        <div class="meta">Chat {d['chat_id']} · {d['message_count']} messages · {d['generated_at']}</div>
        <div class="content">{d['content'].replace(chr(10), '<br>')}</div>
        </div>"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Telegram AI Digest</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:900px;margin:0 auto;padding:20px;background:#f8f9fa}}h1{{color:#2c3e50}}.digest{{background:white;border-radius:8px;padding:20px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}.meta{{color:#7f8c8d;font-size:.85em;margin-bottom:12px}}.content{{line-height:1.6}}</style></head>
<body><h1>📋 Telegram AI Digest</h1>{items or '<p>No digests yet. Run <code>tad run</code> to generate your first digest.</p>'}</body></html>"""
    return HTMLResponse(html)


@app.get("/api/digests")
async def api_digests(chat_id: int | None = Query(None)):
    cfg = get_config()
    store = Storage(cfg.db_path)
    digests = store.list(chat_id=chat_id, limit=50)
    return JSONResponse(digests)


@app.get("/health")
async def health():
    return {"status": "ok"}


def main():
    import uvicorn
    cfg = get_config()
    uvicorn.run(app, host=cfg.server.host, port=cfg.server.port, log_level="info")


if __name__ == "__main__":
    main()
