# Personal Agent Skills

Reusable skills for AI coding assistants. Works with Claude Code, Codex, OpenCode, and any tool supporting the [Agent Skills](https://agentskills.io) standard.

## Available Skills

| Skill | Description |
|-------|-------------|
| `git-repo-setup` | Checklist for new repos - always set local git identity |
| `terminal-recording` | Create terminal recordings with asciinema |
| `senior-engineer-note-maker` | High-readability engineering markdown with aligned tables, ASCII diagrams, citations, and provenance scaffolds |
| `mock-review-html` | Tabbed GitHub-style HTML mockup of held PR review drafts, with real PR context (description, timeline, verbatim diff strips) for pre-posting human review |
| `markdown-doc-enrichment` | Engineering-doc upgrade pass: mermaid over ASCII, admonitions, posterity folds, decision-history versioning, and a red-team fact-check before shipping |
| `html-review-pack` | Self-contained offline HTML artifacts (chat mockups, tabbed packs, decision packs) so humans review outward-bound content in its destination medium before it fires |

## Installation

### Claude Code

```bash
# Install via openskills (recommended)
bun i -g openskills
openskills install Liam-Deacon/agent-skills
openskills sync

# Or manually clone to skills directory
git clone git@github.com:Liam-Deacon/agent-skills.git ~/.claude/skills/personal
```

### OpenAI Codex

```bash
# Clone to Codex skills directory
git clone git@github.com:Liam-Deacon/agent-skills.git ~/.codex/skills/personal

# Or install individual skills
cp -r git-repo-setup ~/.codex/skills/
cp -r src/terminal-recording ~/.codex/skills/
cp -r senior-engineer-note-maker ~/.codex/skills/
```

### OpenCode

```bash
# Clone to OpenCode skills directory
git clone git@github.com:Liam-Deacon/agent-skills.git ~/.config/opencode/skill/personal

# Or use project-local
git clone git@github.com:Liam-Deacon/agent-skills.git .opencode/skills/personal
```

## Usage

Once installed, invoke skills by name:

```
Use the git-repo-setup skill to configure this new repo
```

## Updating

```bash
# Via openskills
openskills install Liam-Deacon/agent-skills  # Re-install overwrites

# Via git
cd ~/.claude/skills/personal && git pull
```
