# Personal Agent Skills

Reusable skills for AI coding assistants. Works with Claude Code, Codex, OpenCode, and any tool supporting the [Agent Skills](https://agentskills.io) standard.

## Available Skills

| Skill | Description |
|-------|-------------|
| `git-repo-setup` | Checklist for new repos - always set local git identity |
| `terminal-recording` | Create terminal recordings with asciinema |

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
