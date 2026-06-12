---
name: html-review-pack
description: Build a single self-contained offline HTML artifact that mimics the destination medium (chat thread, PR review, decision pack, report) so a human can review outward-bound content in context before anything is sent or posted. Use when drafting messages, reviews, or decisions that need sign-off, when asked for a "mockup" or "pack", or whenever held content should be eyeballed as it will actually land.
---

# html-review-pack

Outward-bound content (messages, reviews, decision summaries) reads differently in
its destination medium than in a markdown draft. A review pack closes that gap: one
self-contained HTML file that renders the held content the way it will actually
land, so the human approves or edits with full context, before anything fires.

Related: `mock-review-html` in this repo is the specialised instance for pull
request reviews (GitHub-look tabs, diff strips, pending pills). This skill is the
general craft.

## Variants (pick by destination)

- **Chat-thread mockup** — message boxes styled like the chat product, in send
  order, each followed by a raw-text block for copy-paste, plus a landing note
  describing where each message goes (channel, thread, attachment).
- **Tabbed pack** — one tab per item (per PR, per decision, per document); a tab
  strip, a status header, item content below. Right for "go over these one by one".
- **Decision pack** — tabs for: the decision in one page, the diagram, the
  comparison matrix (inline table, not an image, so it is crisp), options
  considered with verdicts, change summary, next steps. Built to be attached and
  read offline by someone who was not in the room.
- **Report page** — single-column analysis with a summary up top and folded detail.

## Principles (non-negotiable)

1. **Fidelity over beauty.** The pack shows the exact words that will ship. Never
   paraphrase, trim, or improve the held text in the rendering step. If a section
   fails to parse, render it raw in a `<pre>` rather than dropping it.
2. **Self-contained.** One `.html` file: inline CSS, vanilla JS, no CDN, no
   external fonts or images. It must open from `file://` and survive being
   emailed or attached.
3. **Held means visibly held.** A bold status pill (`PENDING — NOTHING SENT`)
   in a sticky header. Nobody should mistake a mockup for a record of something
   sent.
4. **Edits go to the source, not the artifact.** The pack is generated; the held
   drafts are the truth. The human's wording tweaks are applied to the draft
   files and the pack regenerates.

## Build loop

- **Never hand-write the HTML.** Write a small build script (Python, stdlib) that
  parses the draft sources and emits the page: `parse(source) → model`,
  `render(model) → html`, one `emit()`. Deterministic: same inputs, same output —
  that is what makes iteration cheap (edit one draft, re-run, reload).
- **Mini-markdown renderer**: escape raw HTML first, then code spans, bold, links,
  lists, headings, pipe tables; re-enable a small whitelist of tags the
  destination itself allows (`details`, `summary`, `br`). Real-world content uses
  more markdown than your drafts do — render headings and tables or they arrive
  as visible noise.
- **Verify before handing back**: per-item counts in the source equal rendered
  counts; required markers present (`grep -c PENDING`); no external resources;
  spot-check a few content strings verbatim.
- **Render-check**: serve the file (`python3 -m http.server`), screenshot with a
  headless browser, look at the screenshot. A page that "should" render is not a
  checked page. Report the screenshot path.
- **Report ambiguities** the spec did not cover; fold the answers back into the
  spec so the next generation needs no judgement calls.

## Delivery

- Open the file locally for the reviewer; name the path.
- The human reviews in the artifact, gives wording edits in chat (or directly in
  the sources); apply to sources, regenerate, reopen.
- Only after explicit approval does anything fire — and firing is a separate,
  validated step (anchors checked, dry-run printed, then live), never a side
  effect of generating the pack.

## Antipatterns

- ❌ Hand-authored HTML that drifts from the drafts it claims to show.
- ❌ "Improving" the held text during rendering.
- ❌ External CSS/JS/fonts that break offline or leak the content to a CDN.
- ❌ No pending marker, so a screenshot of the mockup reads as a sent record.
- ❌ Editing the artifact instead of the sources.
- ❌ Declaring it renders without looking at a screenshot.
