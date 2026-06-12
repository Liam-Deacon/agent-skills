---
name: senior-engineer-note-maker
description: Create highly human-readable engineering markdown for documentation, PR descriptions, issue descriptions, and PR comments. Use when outputs require aligned markdown tables, ASCII diagrams, evidence-based citations, GitHub permalinks with metadata comments, and heredoc-safe GitHub CLI authoring.
---

# Senior Engineer Note Maker

Produce markdown that is readable in raw form and rendered form, with explicit evidence and traceability.

## Output Rules

1. Use whitespace-aligned markdown tables whenever comparing options, risks, metrics, or outcomes.
2. Use ASCII diagrams for architecture, data flow, lifecycle, and process flow explanations.
3. Use numeric citations `[1]`, `[2]` for factual claims, decisions, and implementation rationale.
4. Prefer inline descriptive links for repo/issue/code references.
5. Use GitHub permalinks with line ranges for code references.
6. Add hidden permalink metadata comments near permalinks:

```html
<!-- permalink-meta: branch=<branch>, timestamp=<ISO8601> -->
```

## Provenance Frontmatter

When generating documentation-style markdown, prepend YAML frontmatter based on the profile in `references/internal-frontmatter-schema.md`.

Author identity priority is fixed:
1. Email
2. Full name
3. Git handle

Use `scripts/render_note_scaffold.sh` to generate compliant scaffolds.

## PR and Comment Authoring

Avoid literal `\\n` in GitHub PR descriptions and comments.
Use heredoc workflows from `scripts/gh_heredoc_templates.sh`.

## Workflow

1. Select artifact type (`doc`, `pr`, `issue`, `comment`).
2. Generate scaffold:

```bash
scripts/render_note_scaffold.sh --type doc --title "Design Note: Example"
```

3. Fill decision details, aligned tables, and ASCII diagrams.
4. Add citations and cross-references.
5. If referencing code, add permalink metadata comments.
6. For GitHub posting, use heredoc templates:

```bash
scripts/gh_heredoc_templates.sh
```

## References

- Style and readability patterns: `references/style-guide.md`
- Citation and cross-reference patterns: `references/citation-patterns.md`
- Permalink and metadata patterns: `references/github-permalink-patterns.md`
- Provenance frontmatter profile: `references/internal-frontmatter-schema.md`
- End-to-end examples: `references/examples.md`

## Validation

Run output checks after scaffold generation:

```bash
scripts/validate_scaffold_output.sh
```
