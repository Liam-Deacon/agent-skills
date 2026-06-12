---
name: mock-review-html
description: Render held/draft PR review text as a single self-contained HTML page that loosely mimics the GitHub review UI, tabbed with one tab per PR, so a human can eyeball exactly how reviews will land before they are posted. Use when asked to mock, preview, or visualise PR review comments, a "review pack", or held review drafts.
---

# mock-review-html

Turn one or more PR review drafts (markdown) into ONE self-contained HTML page that looks
loosely like GitHub's PR review UI: a tab per PR, each tab showing the top-level review
box plus the in-line comments as file-anchored cards. The page is for HUMAN REVIEW of
held drafts before posting — always show a "pending / not posted" marker.

## Input convention

Each draft is a markdown file shaped like:

```markdown
# HELD DRAFT — review for <repo> #<number> (<short title>)

> Fire as: <verdict guidance, e.g. "one GitHub review (Comment)">

## Top-level review body

<paragraphs, may contain `code`, **bold**, [links](url), numbered lists>

## In-line comments

### `path/to/file.py` (anchor description)
> <comment body as one or more blockquote lines>

### `another/file` (second comment, ...)
> <body>
```

Parse leniently: the H1 carries repo + PR number + title; every `###` under
"In-line comments" is one anchored comment whose heading is the file path (strip
backticks) plus an optional parenthetical anchor note; the blockquote lines beneath it
are the comment body. The same file path may appear in multiple `###` headings
(several comments on one file); render each as its own card, distinguished by the
anchor note. Anything in the "Fire as" line containing "request changes"
(case-insensitive) renders the red REQUEST CHANGES pill; otherwise the grey COMMENT pill.

## PR context (use it when present)

If a `context/` directory sits next to the drafts, consume per-PR ground truth:

- `<number>.json` — from `gh pr view <n> --repo <owner>/<repo> --json
  number,url,title,body,baseRefName,headRefName,isDraft,author,createdAt,additions,deletions,changedFiles,comments,reviews,commits`
- `<number>.diff` — `gh pr diff <n>` (unified diff)
- `<number>.review-comments.json` — `gh api repos/<owner>/<repo>/pulls/<n>/comments`
  (existing in-line review comments, each with `path`, `html_url`, `diff_hunk`)

When the caller has not pre-fetched these, fetch them with those exact commands first.
The JSON overrides anything guessed from the draft (title, branches, draft state).

Render per tab, in this order:

1. **PR header**: the title links to `url` (open in new tab). Meta line beneath:
   `opened by <author> on <date> · +<additions> −<deletions> · <changedFiles> files`,
   plus the `head → base` branch chips from the JSON.
2. **Description**: the PR body as the first timeline card (author avatar, "opened
   this pull request", date). Render with the mini-markdown rules. If the body exceeds
   ~40 lines, show the first paragraph and fold the rest in `<details>`.
3. **Timeline**: existing issue comments and reviews merged chronologically, each a
   card with author, date, body, and a small "view on GitHub ↗" link to its `url`.
   Bot entries (vercel, linear-code, datadog, CI/quality bots, `[bot]` suffix)
   collapse to one-line rows (icon, author, date, link) since their bodies are noise;
   human and Copilot review bodies render in full. Existing in-line review comments
   from `review-comments.json` group under their parent review (or a "Review comments"
   row) as a collapsed `<details>` list of `path` links to each `html_url`.
4. **The pending review box** (the held draft) renders AFTER the timeline, where
   GitHub puts a not-yet-submitted review. Make it unmistakably the draft: amber left
   border, the PENDING pill in the header row.
5. **Diff context on pending in-line comments**: for each anchored card, find the
   file's hunks in `<number>.diff` and render 3–8 lines as a GitHub-style diff table
   above the comment: line-number gutter, `+` rows on `#e6ffec`, `-` rows on
   `#ffebe9`, context rows white, monospace, the standard blue hunk header
   (`@@ … @@`) on `#ddf4ff`. Choose the hunk whose content matches what the comment
   quotes (identifier, string literal, env var); if nothing matches, the file's first
   hunk; if the file does not appear in the diff at all (repo-level or doc-wide
   comments), show a muted "no diff context for this anchor" bar instead.
   NEVER fabricate or trim-and-reflow code lines — copy them from the diff verbatim
   (content-verbatim: HTML-escaping the characters for rendering is required, reflowing
   or paraphrasing is not allowed). A "no diff context" bar on a real file path is also
   a useful signal to surface in the report: it usually means the PR does not modify
   that file, so the comment cannot be posted as an in-line anchor and must move to the
   review body when fired.

## Output structure (single .html, inline CSS, vanilla JS, no CDN)

1. **Page chrome**: light GitHub palette — page background `#f6f8fa`, cards `#ffffff`,
   borders `#d0d7de`, text `#1f2328`, muted `#59636e`, link `#0969da`. Font stack:
   `-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif`;
   code/diff in `ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace`.
2. **Sticky header**: page title, a bold amber `PENDING — NOTHING POSTED` pill, and the
   tab strip. One tab per PR labelled `#<number>` with a short slug; active tab gets the
   classic GitHub orange underline (`border-bottom: 2px solid #fd8c73`) and bold text.
3. **Per tab** (when `context/` exists, the order is header → description → timeline →
   pending review box → in-line cards, per the PR-context section):
   - PR title line: repo + `#number`, the PR title (linked to the PR when the URL is
     known), a grey `Draft` chip (omit the chip entirely when the PR is not a draft —
     never render a "Not Draft" chip) and `head → base` branch chips if known.
   - **Review box** (mimic GitHub's review summary): rounded card, header row with a
     32px avatar circle (reviewer initials), `<b>reviewer</b> reviewed` + relative time
     "pending", and the COMMENT / REQUEST CHANGES pill. Body = the top-level review body
     rendered with the mini-markdown rules below.
   - **In-line comments**: each as a GitHub-style anchored card —
     a file header bar (monospace path on `#f6f8fa`, rounded top, with the anchor note
     right-aligned in muted text), THEN a diff context strip sourced from
     `context/<n>.diff` per the PR-context section (or from the draft if it embeds one;
     never invented), then the comment card: small avatar, reviewer name, body. Stack
     the cards in draft order.
4. **Mini-markdown rendering** (regex-level is fine):
   `` `x` `` → `<code>`, `**x**` → `<b>`, `[t](u)` → `<a href>`, blank-line split →
   `<p>`, lines starting `1.`/`-` grouped into `<ol>/<ul>`. Escape raw HTML first.
   Keep paragraphs intact — do NOT reflow or reword the draft text. The page must show
   the exact words that will be posted.

   Real PR bodies and bot/Copilot reviews use more of GitHub-flavoured markdown than
   the drafts do, so the renderer must also handle:
   - `#`–`####` headings → step-sized bold headings (GitHub-ish: h3 ≈ 1.05em bold with
     a little top margin). Never leave literal `#` runs visible.
   - Pipe tables: a run of `|`-delimited lines whose second line is the `|---|`
     separator → a real `<table>` (collapsed borders, `#d0d7de` lines, header row on
     `#f6f8fa`). One table row per source line — never let table rows merge into a
     paragraph.
   - A small whitelist of HTML tags GitHub itself allows in comments, re-enabled
     AFTER escaping: `<details>`, `<summary>`, `<br>`. A `<details>` block in a body
     becomes a real collapsible fold (that is how it behaves on GitHub). Everything
     else stays escaped text.
5. **Tabs JS**: one click handler toggling `.on` classes; no frameworks.
6. **Footer**: file list of the source drafts + generation note.

## Design spec (explicit tokens)

Replicate these values exactly; the goal is "obviously GitHub" at a glance, not
pixel-perfect cloning.

| Token | Value |
|-------|-------|
| Page background | `#f6f8fa` |
| Card background | `#ffffff` |
| Borders | `1px solid #d0d7de`, radius `6px` |
| Text / muted / link | `#1f2328` / `#59636e` / `#0969da` |
| Active tab | `border-bottom: 2px solid #fd8c73`, bold text |
| PENDING pill | bold; text `#9a6700`, bg `#fff8c5`, border `#d4a72c66`, radius `999px` |
| COMMENT pill | bg `#eff1f3`, text `#59636e` |
| REQUEST CHANGES pill | bg `#ffebe9`, text `#cf222e` |
| Draft chip | grey outline chip beside the title; omitted entirely for non-drafts |
| Branch chips | monospace, bg `#ddf4ff`, text `#0969da` |
| Avatars | CSS initial-circles; 32px in review boxes, 24px in timeline and comment cards; background colour from a small hash of the author name |
| Diff rows add / del / context | bg `#e6ffec` / `#ffebe9` / `#ffffff` |
| Diff hunk header (`@@ … @@`) | bg `#ddf4ff`, text `#59636e` |
| Line-number gutters | muted text on `#f6f8fa`; add gutter tinted `#ccffd8`, del gutter `#ffd7d5` |
| Pending review box accent | `border-left: 4px solid #d4a72c` |
| File header bar on comment cards | monospace path on `#f6f8fa`, rounded top corners |
| Fonts | system stack for prose; `ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace` for paths, code and diffs |
| Content column | max-width ~980px, centred; the sticky header spans full width |

Anatomy of one tab, top to bottom: PR header card (linked title, meta line, branch
chips) → DESCRIPTION label + opener card → TIMELINE label + chronological cards and
collapsed bot rows → YOUR PENDING REVIEW label + the amber-accented review box →
the pending in-line comment cards (file bar, diff strip, comment) → footer.
Section labels are small grey uppercase, GitHub-settings style.

## Rules

- **Fidelity over beauty**: never paraphrase, truncate, or "improve" the review text.
  If a draft section fails to parse, render it raw in a `<pre>` inside the tab rather
  than dropping it.
- Self-contained: no external fonts, images, or scripts. Avatars are CSS initial-circles.
- Order tabs as given by the caller (a firing order), else by PR number.
- Render-check if a browser loop is available (`playwright-cli` + `python3 -m http.server`),
  else state that the check was skipped.
- Output path: as instructed by the caller; default `review-pack-mockup.html` next to
  the drafts.

## Replication recipe

How a fresh agent reproduces the artifact, end to end:

1. Collect the draft files matching the input convention and note the caller's tab
   order (a firing order beats PR-number order when given).
2. Fetch the per-PR context into `context/` with the three `gh` commands in the
   PR-context section. If `gh` or the repo is unavailable, proceed from drafts alone;
   the page degrades gracefully (no links, no timeline, no diff strips).
3. Do not hand-write the HTML. Write a build script (Python, stdlib only) with this
   shape, then run it:
   - `parse_draft(path)` → repo, number, title, fire-as verdict, body, and the list
     of (file path, anchor note, body) comments
   - `load_context(n)` → merged dict from the three context files, or `None`
   - `mini_md(text)` → HTML per the mini-markdown rules (escape first; whitelist
     `details`/`summary`/`br` back in; headings, lists, pipe tables)
   - `pick_hunk(diff, path, comment)` → the 3–8 line strip as (kind, old_no, new_no,
     text) rows, chosen by matching identifiers the comment quotes; `None` when the
     file is not in the diff
   - `render_tab(draft, ctx)` per tab, and one `emit()` writing the single file
4. The script must be deterministic: same inputs, same output. That is what makes
   iteration cheap (edit one draft, re-run, reload) and lets a reviewer trust that
   the page matches the drafts.
5. Run the verify checklist below, then the render-check, and hand back: per-check
   results, screenshot paths, and any spec ambiguity you hit, so the spec improves.

## Verify before handing back

- Every draft file produced exactly one tab; per tab, count of `###` comments in the
  source equals the number of anchored cards rendered.
- With `context/`: every tab's title links to the PR `url`; the timeline renders one
  entry per issue comment + review in the JSON (collapsed counts as rendered); every
  diff strip's code lines appear verbatim in `context/<n>.diff` (spot-check a few by
  grep); mini-markdown in real comment bodies did not leak raw HTML.
- `grep -c 'PENDING'` ≥ 1; no `http://` CDN/script tags; file opens from `file://`.
