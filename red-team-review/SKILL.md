---
name: red-team-review
description: Adversarially self-review your own changes before a human sees them, using the checks real reviewers actually block on, then try to refute each finding and report only what survives. Use when asked to "red team review", "red team this", "red team the changes", "red team my work", "review this before I push", "what will review pick up", or before opening or updating a pull request.
---

# red-team-review

Review churn is the cost of a reviewer finding something you could have found. Each round
trip burns a day of calendar time, and the same small set of shapes causes almost all of
it. This skill runs those shapes as ranked checks against your own diff, then attacks each
candidate finding until it either survives with evidence or gets dropped.

Related: `markdown-doc-enrichment` in this repo runs a fact-check pass over prose claims,
and `senior-engineer-note-maker` in this repo formats the write-up. This skill is the
correctness and reachability pass on code, upstream of both.

## What actually stalls a merge

Ranked from a real review corpus. These are not the most common comments, they are the
comments that cost a round trip, which is a different and more useful list. Over 80% of
changes at Google clear review in at most one iteration [[13](#sources)], so a second round
is a signal that something on this list went out unchecked.

1. **A test that would also pass without the change.** The reviewer cannot confirm the
   fix, so they cannot approve, however correct the source is. The most frequent single
   blocker.
2. **Files in the diff that do not serve the stated change.** The reviewer has to separate
   the fix from the noise before they can evaluate anything. Entirely self-inflicted.
3. **An enumeration gap.** The change gates one of several paths that return the same
   data. One missed path makes the whole claim unproven.
4. **A fix that is inert on the path that produced the bug.** The code is correct and
   never executes for the reported case.
5. **A description that overclaims.** Reviewers treat a wrong description as blocking,
   because it aims the next reader at a problem that does not exist.

## Rules of engagement

**Read the diff before you read your own rationale.** Start from the code, not from the
commit message, ticket or the description you drafted. Framing effects on LLM reviewers are
systematic, and confident metadata measurably suppresses detection of real defects
[[6](#sources)]. Form your findings first, then read your own story and check whether it
survives.

**Falsification loop.** For each candidate, spend more effort trying to kill it than you
spent finding it. Ask in order. Is the guard already applied upstream or downstream? Is the
branch reachable from a real caller, or is it dead? Does a type, schema or database
constraint already make the bad input impossible? Does the base branch already behave this
way? Report only what survives all four, and say which ones you checked. A published
adversarial pipeline built on exactly this gate killed roughly 79% of its own candidates
before disclosure [[5](#sources)], so expect to discard most of what you find.

**Ground every finding outside your own head.** Run the test, open the file, cite the line.
Asking a model to think again without external evidence does not work and can make answers
worse [[7](#sources)], and developers using AI assistance in mature repos were 19% slower
while believing they were 20% faster [[11](#sources)]. Self-assessed confidence is not
evidence.

**No scenario, no finding.** Every finding carries a concrete failure scenario. Named
inputs, the path they take, the wrong output or state that results. Write the scenario
first and drop the finding if it will not come out. A finding you cannot instantiate is
usually wrong.

**Precision budget, and a cap.** Google ships a static-analysis check to reviewers only if
it stays under 10% *effective* false positives, where an effective false positive is any
finding the developer took no action on, even a technically correct one [[9](#sources)].
Hold yourself to that. Higher comment volume from automated reviewers correlates with
longer resolution times and lower average feedback quality [[14](#sources)], so cap the
report at roughly ten findings and spend the budget on the top of the ranked list. Never
set yourself a quota to find something.

**Introduced or pre-existing.** Decide for each finding whether the change caused it or
the base branch already had it. Both are worth saying and they are different asks.

**Do not do the linter's job.** Formatting, import order, unused variables and type errors
are caught by tooling in seconds. Run the repo's lint, typecheck and test commands, report
pass or the failure, and spend your attention on logic, reachability and intent.

**Name the single gate.** Close by naming the one thing that must change, separately from
everything merely worth doing. Reviewers are asked to approve once a change improves code
health rather than once it is perfect [[3](#sources)], so a flat list of fifteen items
stalls longer than one clear gate plus a follow-up list. Mark the rest `Nit:`, `Optional:`
or `FYI:` [[4](#sources)].

**Say what is clean.** Findings without a verified-clean list read as unbounded risk, and
the reviewer re-checks everything anyway.

## The ranked checks

Work down. Skip only what the diff cannot reach.

**1. A test that passes without your fix.** Check out the base branch, run the new tests
there, and report the result as "N fail on base, N pass on branch". If they pass on base
they do not test the change. Same class, all seen repeatedly. A test that exercises a
different branch from the one you edited, typically the thrown path when you changed the
returned path. An assertion that restates implementation literals, such as exact-shape
equality on a config object, which then breaks on any harmless addition. A test on code
the framework can never reach, so it is permanently green. Removing the old input and the
old expectation together, so the revised suite also passes against the old
implementation. A timezone or boundary case whose inputs never reach the boundary. Also
check any test-plan checkbox you left unticked, since that alone gets changes requested.

**2. Does your fix actually run on the path that produced the bug?** Trace from the real
entry point to your changed line. Recurring shape. An error class is flattened into a
plain object by an intermediate layer, so the `instanceof` guard you added never matches.
A helper reads a field that is populated on a different object on the path that matters.
Instrumentation added to a file the framework never loads. If the fix cannot fire, say so
rather than shipping a claim.

**3. Read-path authorization and data exposure.** For every new field, relation or route,
enumerate *every* path that returns it, then state the list. The recurring shape is a
filter applied at the top level while an enriched, nested or related object carries the
same data through unfiltered. Also verify a bearer token is checked before it is trusted,
that error payloads carry no raw exception message outward, that any database or
user-sourced string interpolated into HTML or email is escaped, and that a new route has
an audience gate at all.

**4. Files in the diff that do not serve the stated change.** Go file by file and justify
each against the ticket. Formatting-only reflows of files you merely opened, a second
feature bundled in, documentation far larger than the change needs, one-off scripts the
repo keeps local by convention, new shared surface no caller exercises yet. Revert them.
Report the ratio, for example "22 files changed, 6 implement the fix". Calibration. Google
treats roughly 100 lines as a reasonable change and 1000 as too large, and calls 200 lines
spread across 50 files too broad [[2](#sources)]. Reviewers find defects at 200 to 400
lines per sitting and detection falls off sharply beyond that [[10](#sources)], so a large
diff does not get reviewed harder, it gets reviewed worse.

**5. An input the computation reads that is not in the cache key.** For every cache, memo,
query key or persisted derived value, list the inputs the computation actually reads and
diff that against the key. Anything in the first and not the second is a stale read. Two
named variants. Serving a cached result without validating it against the current
selection. Treating an empty collection as "not loaded yet", which silently undoes a
deliberate clear.

**6. The second pass.** Most of the subtle defects live on the re-entry path, not the
first run. Re-editing a record recomputes a "before" snapshot from state the first edit
already cleared, writing null over real audit history. Re-running reuses an owner or id
from the previous run. A retry after partial failure cannot find the half-written records.
Run every new flow twice in your head and check what the second pass reads.

**7. Unbounded work.** Any query with no limit or projection, any loop issuing a round
trip per item, any document or payload that grows with no size check, any polling that can
outlast the request deadline. Give numbers. "One round trip per item, no limit, and the
route sets no maxDuration" is actionable, "consider performance" is not.

**8. The same rule written in more than one place.** Grep every literal, status set and
predicate you added. If the rule now lives in three call sites, all three must move
together next time. Name the existing constant or helper if one exists and say whether it
is exported. This comes back constantly as "that value is now hardcoded a fourth time".

**9. Comments.** Sort every comment you added into four buckets and act. Delete the ones
that restate the code. De-duplicate rationale now appearing near-verbatim in two or more
places, keeping the copy nearest the decision. Shorten real reasoning written as an essay.
Keep load-bearing WHY and say which ones those are, because reviewers do defend a
genuinely useful comment.

**10. Dates, timezones and boundaries.** `new Date('2026-08-12')` parses as UTC while
`new Date(2026, 7, 12)` parses as local, and month-span arithmetic differs between them.
Check month ends, inclusive versus exclusive bounds, and whether your timezone test
actually discriminates against the pre-fix behaviour instead of passing both ways.

**11. Repo conventions.** Read the repo's agent instructions, contributing guide and
neighbouring files before asserting a convention. Recurring shapes. Bypassing a mandated
data-access or service layer. A filename that does not match its exported symbol. Adding a
code to one registry and not its paired one. Not listing a new artifact in the canonical
index that names its peers. Cite the rule and where it lives.

**12. Legacy persisted shapes.** If you tightened a parse, filter or schema, find out what
is already stored. A stricter reader silently discards the older shape and saved records
then render as zero, blank or missing. Query or grep the real distribution and give the
count of affected records. A count turns an argument into a fact.

**13. Claims in the description, docs and links.** Verify every factual claim in your own
description against the code, including each "this previously did X". Check that
referenced files, ADRs and screenshots exist on the branch, that links use commit SHAs
rather than mutable branch refs, and that committed screenshots still match the UI after
your later commits.

**14. Dead code and unexercised new surface.** Anything you added that nothing calls,
anything you made unreachable, any prop, slot or flag plumbed through with no consumer.
Confirm reachability from a real entry point before instrumenting or testing something. A
test on unreachable code is worse than none, because it encodes a false model of the
runtime. Also check that a feature flag or kill switch covers every surface the change
adds, including the one that mutates historical records.

**15. Framework state and identity.** In React, the recurring ones. An unmemoised value
added to a `useMemo` or `useCallback` dependency array, which silently disables the memo
you just edited. State not reset when the entity identity changes, with no `key` to force
it. A ref populated only inside a fetch function, so cache hits keep the previous entity's
value. A handler recreated each render, defeating a `React.memo` below it. Comparisons
that are `undefined === undefined` and therefore true while a value is still loading. For
anything deeper hand off to `vercel:react-best-practices`.

**16. Atomicity, and parity between a preview and its mutation.** Multi-step writes with
no transaction and no compensating action leave records half-applied and unaudited, and a
retry will not find them. Separately, if the change has a dry run, a preview count or a
typed confirmation, verify the predicate is defined once and shared by both paths. A
confirmation gate is only safe when the number the operator confirms is the number that
changes.

## Compose, do not duplicate

Run this pass for reachability and correctness, then hand specialist surfaces over rather
than half-doing them here.

| Surface in the diff | Reach for |
|---|---|
| React or Next.js components, hooks, data fetching | `vercel:react-best-practices` |
| Auth, secrets, injection, a dedicated security pass | `/security-review` |
| A GitHub PR rather than your working diff | `/review` |
| Quality-only cleanups, reuse and simplification | `simplify`, which does not hunt bugs |
| UI, keyboard and screen-reader behaviour | `a11y-audit`, `web-design-guidelines` |
| Core Web Vitals, bundle and runtime cost | `performance`, `vercel:vercel-optimize` |
| Lockfile or dependency changes | `dep-lock-audit` |
| ADRs and design docs the change touches | `markdown-doc-enrichment` |
| Writing the findings up for a human | `senior-engineer-note-maker` |
| Eyeballing the report before it is posted | `mock-review-html`, `html-review-pack` |

## Reporting

Split into **Blocking** and **Non-blocking**, blocking first, ordered by severity rather
than by file. Each finding gets five things and nothing else.

1. **Severity, and introduced or pre-existing.**
2. **`path/to/file.ext:LINE`.** The line, not the file.
3. **The failure scenario.** Named inputs, the path, the wrong output. One or two sentences.
4. **The smallest fix.** Often one line. Write it as a fragment or diff when short enough
   to be unambiguous.
5. **How you tried to refute it**, from the falsification loop.

Then three short closing sections. **The gate**, naming the one item that must change.
**Checked and clean**, listing what you verified with the evidence, including lint,
typecheck and test results. **Withdrawn**, listing candidates you dropped and what killed
each one. The withdrawn list is what makes the rest of the report credible.

## Antipatterns

- ❌ A finding with no inputs that reach the bad output.
- ❌ A quota. Requiring yourself to find N issues manufactures false positives.
- ❌ Reporting a linter or typechecker finding as review substance.
- ❌ Reporting a base-branch defect without saying it is pre-existing.
- ❌ Claiming a test covers the fix without running it against the base branch.
- ❌ A findings list with no clean list and no withdrawn list.
- ❌ Fifteen items and no named gate.
- ❌ "Consider whether X" when you had the code and could have checked X.
- ❌ Reviewing the description you wish you had written instead of the diff you have.

## Sources

The ranked checks come from a corpus of roughly 200 pull requests on a production
TypeScript monorepo, about 350 reviewer comments across one senior human reviewer and three
automated reviewers, clustered by observed frequency and weighted by which comments actually
cost a round trip. The external evidence below shaped the rules of engagement.

1. Google, [Code Review Developer Guide](https://google.github.io/eng-practices/review/) and [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html).
2. Google, [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) and [Writing good CL descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html), which also says to review the description itself before submitting.
3. Google, [The standard of code review](https://google.github.io/eng-practices/review/reviewer/standard.html). Approve once it improves code health, because there is no perfect code.
4. Google, [How to write code review comments](https://google.github.io/eng-practices/review/reviewer/comments.html). Source of the `Nit:` and `Optional:` prefixes.
5. Agarwal, [Refute-or-Promote: an adversarial stage-gated multi-agent review methodology](https://arxiv.org/abs/2604.19049), 2026. Adversarial kill mandates and context asymmetry, killing roughly 79% of candidates pre-disclosure.
6. Mitropoulos et al., [Measuring and exploiting contextual bias in LLM-assisted security code review](https://arxiv.org/abs/2603.18740), 2026. Framing effects are systematic, and metadata redaction restores detection.
7. Huang et al., [Large language models cannot self-correct reasoning yet](https://arxiv.org/abs/2310.01798), ICLR 2024.
8. Mäntylä and Lassenius, [What types of defects are really discovered in code reviews?](https://dl.acm.org/doi/10.1109/TSE.2008.71), IEEE TSE 2009. About 75% of review findings do not affect visible functionality, which is why comments, duplication and convention earn places on the list.
9. Sadowski et al., [Static analysis](https://abseil.io/resources/swe-book/html/ch20.html), Software Engineering at Google ch. 20. The 10% effective-false-positive bar, and showing warnings only on newly introduced lines.
10. SmartBear and Cisco, [Best practices for peer code review](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/). 200 to 400 lines per sitting, with detection falling off after 60 to 90 minutes.
11. METR, [Measuring the impact of early-2025 AI on experienced open-source developer productivity](https://arxiv.org/abs/2507.09089), 2025. 19% slower while feeling 20% faster.
12. GitHub, [Helping others review your changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/helping-others-review-your-changes). The vendor case for self-review before requesting review.
13. Sadowski et al., [Modern code review: a case study at Google](https://research.google/pubs/modern-code-review-a-case-study-at-google/), ICSE-SEIP 2018. Over 80% of changes take at most one review iteration, so more than one round trip is a signal, not a norm.
14. Fatima et al., [On the footprints of reviewer bots feedback on agentic pull requests](https://arxiv.org/abs/2604.24450), 2026. Higher bot comment volume tracks longer resolution and lower feedback quality.
15. Yu et al., [Habituation at the gate](https://arxiv.org/abs/2606.22721), 2026. Human scrutiny of agent-authored code decays with exposure, so the author-side pass carries more weight over time.

Closest published prior art, and why this skill is not it. Anthropic's [code-review plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) runs parallel agents, scores each issue for confidence and drops anything under 80, but it operates on an open pull request after the human is already in the loop, and confidence is asserted by the finder rather than attacked. [claude-code-security-review](https://github.com/anthropics/claude-code-security-review) has an exemplary dedicated false-positive filter but covers security only. Community adversarial-review skills tend to run several personas and escalate on agreement, and at least one instructs every persona to find at least one issue, which guarantees false positives. This skill runs before the human is invited, mandates refutation, requires execution-grounded evidence, and caps output.
