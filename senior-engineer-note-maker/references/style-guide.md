# Style Guide

## Primary Goal

Maximize reader comprehension without requiring markdown rendering.

## Table Rules

- Align pipes and cell spacing so tables remain legible in raw markdown.
- Use short headers.
- Keep one fact per cell.

Example:

```markdown
| Option | Complexity | Risk | Notes |
| ------ | ---------- | ---- | ----- |
| A      | Low        | Low  | Fast rollout |
| B      | Medium     | High | Migration required |
```

## Diagram Rules

Use ASCII diagrams for high-level flow before detailed sections.

```text
Client --> API --> Service --> DB
```

## Section Order

1. Context
2. Decision / Proposal
3. Comparison summary (table)
4. Architecture/flow (ASCII)
5. Risks and mitigations
6. Evidence and citations
7. Next actions
