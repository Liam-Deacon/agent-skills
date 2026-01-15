---
name: git-repo-setup
description: Personal checklist for setting up new git repositories. Always configure local git identity to avoid commits with incorrect email.
---

# Git Repo Setup

Use this skill when creating or cloning a new repository.

## Required: Set local git identity

Every new repo must have explicit git config for name and email:

```bash
git config user.name "Liam Deacon"
git config user.email "<appropriate-email>"
```

### Email selection

| Repo org | Email |
|----------|-------|
| AntarcticaAM | liam@antarcticaam.com |
| Personal / Other | liam.m.deacon@gmail.com |

## Why this matters

Without explicit config, git falls back to global config or auto-detected values (e.g., `liam@mac.home`), which:
- Breaks GitHub contribution attribution
- Looks unprofessional in commit history
- May leak machine hostnames

## Quick setup for new repos

### New AntarcticaAM repo
```bash
gh auth switch --user LiamDeaconAntarcticaAM
gh repo create AntarcticaAM/repo-name --private
cd repo-name
git config user.name "Liam Deacon"
git config user.email "liam@antarcticaam.com"
```

### New personal repo
```bash
gh auth switch --user Liam-Deacon
gh repo create repo-name --private
cd repo-name
git config user.name "Liam Deacon"
git config user.email "liam.m.deacon@gmail.com"
```

## Fixing incorrect commits

If commits were made with wrong email:
```bash
git commit --amend --reset-author --no-edit
git push --force  # Only if already pushed
```
