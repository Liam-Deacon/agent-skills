---
name: markdown-doc-enrichment
description: Upgrade engineering markdown (ADRs, design docs, platform overviews, decision records) so it renders well on GitHub and survives scrutiny — mermaid over ASCII, admonitions for load-bearing callouts, details-folds for posterity content, decision-history versioning, and a red-team fact-check pass before shipping. Use when writing or amending ADRs, architecture docs, comparison matrices, or any doc that records a decision someone may later contest.
---

# markdown-doc-enrichment

Engineering docs fail two ways: they render as walls of monospace nobody reads, or
they assert things nobody verified. This skill fixes both. It applies to ADRs,
design docs, platform overviews, migration guides, and decision records — anything
where a future reader needs to trust both the rendering and the claims.

## Diagrams

- **Mermaid over ASCII** wherever GitHub renders it well: flowcharts, sequence
  diagrams, simple architecture. ASCII art breaks at the first edit and reads as
  neglect; mermaid diffs cleanly and renders natively.
- **Complex diagrams that mermaid handles badly** (dense matrices, styled trees for
  non-technical audiences): build an HTML artifact, render it to PNG/SVG with a
  headless browser, and **commit the image** under an assets convention next to the
  docs (`docs/<area>/assets/<topic>/<name>.png`), embedded with a relative path.
  Keep the HTML source somewhere regenerable; the image and the doc must change in
  the same commit when content changes (a matrix image rendered before a verdict
  row was added is a lie).
- Private repos: committed images render in Files view and rendered docs;
  comment-attachment URLs do not survive in private repos, so never rely on them
  for doc content.

## Admonitions (load-bearing callouts)

Use GitHub admonitions for the sentences that carry the decision:

- `> [!IMPORTANT]` — the agreed decision, its revisit clause, anything a reader
  must not skim past.
- `> [!WARNING]` — ruled-out options and the reason, so nobody re-proposes them
  innocently.
- `> [!NOTE]` — standing rules, grandfathering, conventions that survive the doc.

One admonition per point. A page of admonitions is a page of body text.

## Posterity folds

Decisions age better when the reasoning stays present but folded:

- Keep **verdicts visible**: a comparison matrix keeps every option as a column and
  gains an **Outcome row** (adopted / parked with revisit condition / ruled out with
  reason). Deleting losing options invites relitigating them.
- Fold the long-form rationale in `<details><summary>` blocks: prior-version
  reasoning, measured-evidence appendices, alternatives considered. The bar: a
  reader can see things WERE considered and that the decision rests on named
  constraints, without wading through them.
- Never fold the decision itself, the revisit clause, or the decision history.

## Versioning and decision history

When a decision doc changes materially:

- Frontmatter gains `version` (bump major on a changed decision, minor on scope or
  clarity changes) and `updated_at`.
- Add a `## Decision history` section: one line per version — date, what changed,
  why. This is how a reader learns the v1 proposal was rescoped without spelunking
  git.
- **Statuses stay honest.** A decision agreed verbally is `proposed` until the
  ratification mechanism (usually peer review of the amending PR) completes. Do not
  mark `accepted` because a meeting went well; record "agreed in the <date> session;
  ratification is approval of this PR".

## The red-team pass (before shipping, always)

Silently verify, in place, before the doc goes out:

1. **Every number** (caps, limits, line counts, durations) against its source.
2. **Every reference**: PR/issue numbers resolve to what the prose claims;
   cross-repo references are fully qualified (`owner/repo#123` — a bare `#123`
   points into whatever repo hosts the doc).
3. **Every quote and attribution**: people only said what the transcript says;
   prefer "the session left X open" over "we agreed X" unless the words exist.
4. **Every date**: relative dates become absolute; day-of-week claims are checked
   against a calendar (wrong-day errors are common and corrosive).
5. **Every named artifact still exists**: files, flags, classes, packages get a
   grep before the doc asserts them.
6. Claims that fail verification get fixed or hedged — never shipped on vibes.

Do not advertise the pass in the doc; the output is correctness, not a section
about correctness.

## Voice

Plain prose. No em dashes, no theatrical colons or semicolons, no bullet-summary
endings that restate the document. Short sentences, commas where needed. Every
criticism of an alternative is paired with the constraint that killed it.

## Antipatterns

- ❌ ASCII "figures" in docs that GitHub would render as mermaid.
- ❌ Deleting ruled-out options instead of recording their verdicts.
- ❌ `status: accepted` on the strength of a conversation.
- ❌ Bare `#123` cross-repo references.
- ❌ A matrix image that lags the matrix it pictures.
- ❌ Shipping a number, date, or quote nobody checked.
