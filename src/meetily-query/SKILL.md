---
id: agent-skills/meetily-query
title: "Query Meetily Meeting Data"
summary: "Extract meetings, transcripts, and AI summaries from Meetily's local SQLite database"
repo: agent-skills
path: src/meetily-query/SKILL.md
type: data-access
intended_audience:
  - backend-engineer
  - data-engineer
  - ai-engineer
status: active
visibility: public
created_at: 2026-05-19
updated_at: 2026-05-19
authors:
  - "@Liam-Deacon"
when_to_use: "When you need to search, read, or process meeting transcripts and summaries stored locally by the Meetily app"
capabilities: "List meetings, retrieve full transcripts with timestamps, read AI-generated summaries and action items"
technologies: "SQLite, Python, Meetily, macOS"
related_skills: []
---

# Query Meetily Meeting Data

## Overview

Meetily stores all meeting data in a plain SQLite database on macOS. No encryption, no API required. This skill covers querying it directly from scripts or agent tool calls.

## Database Location

```
~/Library/Application Support/com.meetily.ai/meeting_minutes.sqlite
```

Assign this to a variable to avoid repetition:

```bash
DB="$HOME/Library/Application Support/com.meetily.ai/meeting_minutes.sqlite"
```

## Schema

| Table | Purpose |
|---|---|
| `meetings` | One row per meeting: `id`, `title`, `created_at`, `folder_path` |
| `transcripts` | Chunked transcript lines with `speaker`, `transcript`, `audio_start_time`, `audio_end_time` |
| `summary_processes` | AI summary output as JSON in `result` column, plus `status` and `processing_time` |
| `meeting_notes` | User-edited notes as `notes_markdown` and `notes_json` |

## Common Queries

### List all meetings

```bash
sqlite3 "$DB" "SELECT id, title, created_at FROM meetings ORDER BY created_at DESC;"
```

### Full transcript for a meeting (ordered by time)

```bash
sqlite3 "$DB" "
SELECT speaker, transcript, audio_start_time
FROM transcripts
WHERE meeting_id = '<meeting-id>'
ORDER BY audio_start_time;
"
```

### Get the AI summary

```bash
sqlite3 "$DB" "
SELECT json_extract(result, '$.markdown')
FROM summary_processes
WHERE meeting_id = '<meeting-id>' AND status = 'completed';
"
```

### Meeting durations at a glance

```bash
sqlite3 "$DB" "
SELECT m.title,
       COUNT(t.id) AS chunks,
       ROUND((MAX(t.audio_end_time) - MIN(t.audio_start_time)) / 60.0, 1) AS duration_min
FROM meetings m
JOIN transcripts t ON t.meeting_id = m.id
GROUP BY m.id, m.title
ORDER BY m.created_at DESC;
"
```

## Python Helper

Use this to get a full meeting transcript as a list of dicts:

```python
import sqlite3
from pathlib import Path

DB = Path.home() / "Library/Application Support/com.meetily.ai/meeting_minutes.sqlite"

def list_meetings(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT id, title, created_at FROM meetings ORDER BY created_at DESC"
    ).fetchall()
    return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]

def get_transcript(conn: sqlite3.Connection, meeting_id: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT speaker, transcript, audio_start_time, audio_end_time
        FROM transcripts
        WHERE meeting_id = ?
        ORDER BY audio_start_time
        """,
        (meeting_id,),
    ).fetchall()
    return [
        {"speaker": r[0], "text": r[1], "start": r[2], "end": r[3]}
        for r in rows
    ]

def get_summary(conn: sqlite3.Connection, meeting_id: str) -> str | None:
    row = conn.execute(
        """
        SELECT json_extract(result, '$.markdown')
        FROM summary_processes
        WHERE meeting_id = ? AND status = 'completed'
        """,
        (meeting_id,),
    ).fetchone()
    return row[0] if row else None

# Usage
with sqlite3.connect(DB) as conn:
    meetings = list_meetings(conn)
    for m in meetings:
        print(m["title"])
        summary = get_summary(conn, m["id"])
        if summary:
            print(summary[:300])
```

## Notes

- `transcripts.speaker` is often empty -- Meetily's speaker diarization is optional and model-dependent.
- The `result` column in `summary_processes` is a JSON string with a `markdown` key. Use `json_extract` in SQLite or `json.loads` in Python.
- Audio timestamps are in seconds from the start of the recording, not wall-clock time.
- The DB path uses bundle ID `com.meetily.ai` -- do not rely on the `meetily` directory under Application Support, which only holds notifications.
