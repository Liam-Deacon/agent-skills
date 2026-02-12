# Frontmatter Profile (Relaxed Compatibility)

This skill uses a stage-doc style frontmatter profile and intentionally relaxes strict author regex validation to preserve provenance richness.

## Required Fields

Every documentation scaffold should include:

| Field | Required | Notes |
| ----- | -------- | ----- |
| `id` | yes | `{repo}/{slug}` style identifier |
| `title` | yes | Human-readable title |
| `summary` | yes | 1-3 sentence summary |
| `repo` | yes | Source repository |
| `path` | yes | `docs/.../*.md` style path |
| `type` | yes | `documentation`, `adr`, `runbook`, `guide`, `reference`, `rfc`, `prd`, `deprecation` |
| `category` | yes | Team category taxonomy |
| `intended_audience` | yes | One or more audience tags |
| `status` | yes | `active`, `draft`, `deprecated`, `archived` |
| `visibility` | yes | `internal`, `public`, `restricted` |
| `created_at` | yes | ISO date |
| `updated_at` | yes | ISO date |
| `authors` | yes | Ordered by identity priority (below) |
| `sync` | yes | Boolean sync indicator |

## Author Identity Resolution

Resolve each author using this strict priority:

1. Email
2. Full name
3. Git handle

Example:

```yaml
authors:
  - "engineer@example.com"
  - "Engineer Name"
  - "@engineerhandle"
```

If only one format is available, use it directly.

## Optional Provenance Fields

Include when known:

- `source_files`
- `related_docs`
- `tags`
- `owner_team`
- `version`
- `review_frequency`
