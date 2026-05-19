---
id: agent-skills/meetily-mcp
title: "Build a Meetily MCP Server"
summary: "Expose Meetily meeting transcripts and summaries to AI agents via a local MCP server"
repo: agent-skills
path: src/meetily-mcp/SKILL.md
type: integration
intended_audience:
  - ai-engineer
  - backend-engineer
status: active
visibility: public
created_at: 2026-05-19
updated_at: 2026-05-19
authors:
  - "@Liam-Deacon"
when_to_use: "When you want to query Meetily meeting data from Claude Code, Cursor, or any MCP-compatible AI agent without writing ad-hoc SQL"
capabilities: "list_meetings, get_transcript, get_summary tools exposed over MCP stdio transport"
technologies: "MCP, Python, SQLite, Meetily, macOS"
related_skills: ["agent-skills/meetily-query"]
---

# Build a Meetily MCP Server

## Overview

Meetily has no official MCP server. This skill builds a minimal one that reads from Meetily's local SQLite database and exposes three tools to any MCP client (Claude Code, Cursor, Windsurf, etc.).

See [`agent-skills/meetily-query`](../meetily-query/SKILL.md) for the underlying database schema.

## Prerequisites

```bash
pip install mcp  # or: uv add mcp
```

## Implementation

Create `meetily_mcp.py` (single file, no framework needed):

```python
#!/usr/bin/env python3
"""Minimal MCP server for Meetily meeting data."""

import json
import sqlite3
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

DB = Path.home() / "Library/Application Support/com.meetily.ai/meeting_minutes.sqlite"

app = Server("meetily")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_meetings",
            description="List all recorded meetings with title, id, and date",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_transcript",
            description="Get the full transcript for a meeting, ordered by time",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "string", "description": "The meeting id from list_meetings"}
                },
                "required": ["meeting_id"],
            },
        ),
        Tool(
            name="get_summary",
            description="Get the AI-generated markdown summary for a meeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "meeting_id": {"type": "string", "description": "The meeting id from list_meetings"}
                },
                "required": ["meeting_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    with _connect() as conn:
        if name == "list_meetings":
            rows = conn.execute(
                "SELECT id, title, created_at FROM meetings ORDER BY created_at DESC"
            ).fetchall()
            result = [dict(r) for r in rows]

        elif name == "get_transcript":
            meeting_id = arguments["meeting_id"]
            rows = conn.execute(
                """
                SELECT speaker, transcript AS text, audio_start_time AS start_s
                FROM transcripts
                WHERE meeting_id = ?
                ORDER BY audio_start_time
                """,
                (meeting_id,),
            ).fetchall()
            result = [dict(r) for r in rows]

        elif name == "get_summary":
            meeting_id = arguments["meeting_id"]
            row = conn.execute(
                """
                SELECT json_extract(result, '$.markdown') AS markdown
                FROM summary_processes
                WHERE meeting_id = ? AND status = 'completed'
                """,
                (meeting_id,),
            ).fetchone()
            result = {"markdown": row["markdown"] if row else None}

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

## Register with Claude Code

Add to `~/.claude/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "meetily": {
      "command": "python3",
      "args": ["/path/to/meetily_mcp.py"]
    }
  }
}
```

Or with `uv run` for dependency isolation:

```json
{
  "mcpServers": {
    "meetily": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "/path/to/meetily_mcp.py"]
    }
  }
}
```

Then restart Claude Code. The three tools will appear as `mcp__meetily__list_meetings`, `mcp__meetily__get_transcript`, and `mcp__meetily__get_summary`.

## Extending

To add search across transcripts:

```python
Tool(
    name="search_transcripts",
    description="Full-text search across all meeting transcripts",
    inputSchema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
),
```

```python
elif name == "search_transcripts":
    query = arguments["query"]
    rows = conn.execute(
        """
        SELECT m.title, m.created_at, t.transcript AS text, t.audio_start_time AS start_s
        FROM transcripts t
        JOIN meetings m ON m.id = t.meeting_id
        WHERE t.transcript LIKE ?
        ORDER BY m.created_at DESC, t.audio_start_time
        LIMIT 50
        """,
        (f"%{query}%",),
    ).fetchall()
    result = [dict(r) for r in rows]
```

## Notes

- The server reads only -- no writes to the Meetily DB.
- Meetily must be installed and have run at least one meeting for the DB to exist.
- Transcripts can be large (1500+ rows for a long meeting). Consider adding a `limit` parameter to `get_transcript` if context window size is a concern.
