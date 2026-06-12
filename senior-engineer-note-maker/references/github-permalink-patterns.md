# GitHub Permalink Patterns

## Code Links

Use permalinks with line ranges when highlighting behavior.

```markdown
The retry loop ignores 429 backoff in
[`worker.py#L84-L113`](https://github.com/myorg/myrepo/blob/abc123/path/worker.py#L84-L113).
<!-- permalink-meta: branch=feature/retry-fix, timestamp=2026-02-12T15:20:00Z -->
```

## Metadata Comment Rule

Always place metadata comment immediately after the permalink paragraph.

Required keys:

- `branch`
- `timestamp` (ISO8601 UTC preferred)
