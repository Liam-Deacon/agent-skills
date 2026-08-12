---
id: agent-skills/asciinema-recording
title: "Terminal Session Recording with asciinema"
summary: "Creating and sharing terminal session recordings for documentation and demonstration"
repo: agent-skills
path: SKILL.md
type: documentation
intended_audience:
  - backend-engineer
  - frontend-engineer
  - devops-engineer
  - technical-writer
status: active
visibility: internal
created_at: 2025-01-14
updated_at: 2025-01-14
authors:
  - "@LiamDeaconAntarcticaAM"
when_to_use: "When creating tutorials, demos, documentation, or troubleshooting guides that benefit from visual terminal session recordings"
capabilities: "Record terminal sessions with timing, convert to GIF/MP4, share locally or upload to approved platforms only"
technologies: "asciinema, agg, ffmpeg, terminal, bash/zsh"
related_skills: []
---

# Terminal Session Recording with asciinema

## Overview

This skill covers creating professional terminal session recordings for documentation, tutorials, and demonstrations using asciinema. Recordings capture timing, commands, and output for playback or conversion to video formats.

## Critical Safety Notice

**🚨 NEVER UPLOAD TO asciinema.org UNLESS EXPLICITLY STATED**

- Recordings contain sensitive information (API keys, credentials, file paths)
- Always share locally or through approved internal channels only
- Default to local playback and conversion to GIF/MP4 for sharing

## Prerequisites

```bash
# Install asciinema
brew install asciinema

# Install conversion tools (optional)
brew install ffmpeg
npm install -g asciinema-agg  # or use agg directly
```

## Basic Recording

### Start Recording

```bash
# Start recording (saves to ~/recordings/)
asciinema rec demo.cast

# Or specify filename
asciinema rec my-demo.cast
```

### During Recording

```bash
# Your terminal session here
echo "Hello World"
ls -la
# ... commands you want to record
```

### Stop Recording

```bash
# Press Ctrl+D or type 'exit'
exit
```

## Playback and Verification

### Local Playback

```bash
# Play recording
asciinema play demo.cast

# Play with custom speed
asciinema play -s 2 demo.cast  # 2x speed

# Play without pausing at end
asciinema play --no-loop demo.cast
```

### Convert Format (Recommended for Sharing)

```bash
# Convert to v2 format first (for compatibility)
asciinema convert -f asciicast-v2 demo.cast demo-v2.cast

# Convert to GIF
agg demo-v2.cast demo.gif

# Convert to MP4 (better for GitHub)
agg demo-v2.cast demo.gif
ffmpeg -i demo.gif -movflags +faststart -pix_fmt yuv420p demo.mp4
```

## Advanced Recording Techniques

### Record with Custom Settings

```bash
# Record with specific dimensions
asciinema rec --cols 120 --rows 30 demo.cast

# Record with idle time limit
asciinema rec --idle-time-limit 5 demo.cast  # Stop after 5s idle
```

### Edit Recording Before Conversion

```bash
# Convert to editable JSON format
asciinema convert -f asciicast-v2 demo.cast demo.json

# Edit timing/output in JSON if needed
# Then convert back: asciinema convert demo.json demo-final.cast
```

### Font Selection for Professional Output

```bash
# Use Nerd Font for fancy glyphs
agg --font-family "MesloLGS Nerd Font Mono" demo.cast demo.gif

# Or Hack Nerd Font
agg --font-family "Hack Nerd Font Mono" demo.cast demo.gif

# Check available fonts
fc-list :family | grep -i "nerd"
```

## Sharing Methods

### ✅ Safe Sharing (Recommended)

```bash
# 1. Convert to MP4 for GitHub PR comments
asciinema convert -f asciicast-v2 demo.cast demo-v2.cast
agg --font-family "MesloLGS Nerd Font Mono" demo-v2.cast demo.gif
ffmpeg -i demo.gif -movflags +faststart -pix_fmt yuv420p demo.mp4

# 2. Upload MP4 to PR comment via GitHub web UI
# Drag and drop demo.mp4 into comment box

# 3. Reference in documentation
# "See demo.mp4 for visual demonstration"
```

### ❌ Never Do This (Unless Explicitly Approved)

```bash
# DO NOT RUN THIS
asciinema upload demo.cast
asciinema auth
```

## Common Use Cases

### ESLint Rule Demonstration

```bash
# Record ESLint rule testing
asciinema rec eslint-demo.cast
cd /path/to/project
bun nx lint --help
bun nx lint
# Show violations and fixes
exit

# Convert for PR
asciinema convert -f asciicast-v2 eslint-demo.cast eslint-demo-v2.cast
agg --font-family "MesloLGS Nerd Font Mono" eslint-demo-v2.cast eslint-demo.gif
ffmpeg -i eslint-demo.gif -movflags +faststart -pix_fmt yuv420p eslint-demo.mp4
```

### Build Process Documentation

```bash
# Record build demo
asciinema rec build-demo.cast
make build
make test
make deploy
exit

# Convert and share
asciinema convert -f asciicast-v2 build-demo.cast build-demo-v2.cast
agg build-demo-v2.cast build-demo.gif
```

### Troubleshooting Guide

```bash
# Record debugging session
asciinema rec debug-demo.cast
# Show problem
command_that_fails
# Show investigation
logs_and_debugging
# Show solution
fixed_command
exit
```

## File Management

### Organization

```bash
# Create recordings directory
mkdir -p ~/recordings

# Record to organized location
asciinema rec ~/recordings/$(date +%Y%m%d)-eslint-demo.cast

# Archive old recordings
find ~/recordings -name "*.cast" -mtime +30 -exec gzip {} \;
```

### Cleanup

```bash
# Remove temporary files after conversion
rm demo.cast demo-v2.cast demo.gif  # Keep only MP4

# Compress for storage
gzip demo.cast  # Reduces size significantly
```

## Best Practices

### Recording Tips

- **Clear terminal first**: `clear` before starting important parts
- **Slow down for complex commands**: Type deliberately, pause between steps
- **Use descriptive filenames**: `eslint-rules-demo.cast`, `build-process.cast`
- **Test playback**: Always verify recording before sharing
- **Include context**: Add comments or echo statements for clarity

### Quality Settings

```bash
# Recommended settings for demos
asciinema rec \
  --cols 120 \
  --rows 30 \
  --idle-time-limit 10 \
  --command "zsh" \
  demo.cast
```

### Conversion Optimization

```bash
# High quality MP4 for professional sharing
ffmpeg -i demo.gif \
  -movflags +faststart \
  -pix_fmt yuv420p \
  -vf "scale=1190:1344" \
  -r 20 \
  demo.mp4
```

## Troubleshooting

### Recording Issues

```bash
# If recording doesn't start
asciinema --version  # Check installation
which asciinema      # Check PATH

# If terminal looks wrong in playback
asciinema rec --cols 120 --rows 30 demo.cast  # Set explicit dimensions
```

### Conversion Problems

```bash
# If agg fails with font errors
agg --font-family "Monaco" demo.cast demo.gif  # Use system font

# If ffmpeg fails
ffmpeg -i demo.gif demo.mp4  # Simpler conversion

# If file is too large
ffmpeg -i demo.gif -vf "scale=iw/2:ih/2" -r 15 demo-small.mp4
```

### Playback Issues

```bash
# If playback is too fast/slow
asciinema play -s 0.5 demo.cast  # Half speed
asciinema play -s 2 demo.cast    # Double speed

# If colors look wrong
export TERM=xterm-256color
asciinema play demo.cast
```

## Security Considerations

### Sensitive Data

- **Never record sessions with credentials**
- **Clear history before recording**: `history -c`
- **Use environment variables, not hardcoded values**
- **Blur/redact sensitive output in post-processing**

### Sharing Guidelines

- **Internal sharing only**: Slack, internal docs, GitHub PRs
- **No public uploads**: Unless explicitly approved for documentation
- **Verify content**: Review recording before sharing
- **Compress for transfer**: Use MP4 format for smaller files

## Integration with Development Workflow

### Pre-commit Integration

```bash
# Add to .pre-commit-config.yaml for documentation checks
- repo: local
  hooks:
  - id: validate-asciinema
    name: Validate asciinema recordings
    entry: python -c "import sys; print('Recording validation would go here')"
    files: \.cast$
```

### CI/CD Integration

```yaml
# GitHub Actions - validate recordings
- name: Validate asciinema recordings
  run: |
    find . -name "*.cast" -exec asciinema play --no-loop {} \;
```

## Resources

### Documentation
- [asciinema documentation](https://docs.asciinema.org/)
- [agg documentation](https://github.com/asciinema/agg)

### Alternative Tools
- `termtosvg`: Terminal to SVG conversion
- `ttyrec` + `ttygif`: Alternative recording tools
- Screen recording software for complex demos

### Examples
- ESLint rule demonstrations
- Build process documentation
- Troubleshooting guides
- API testing walkthroughs
- Database migration demos

---

## Quick Reference

```bash
# Record
asciinema rec demo.cast

# Play back
asciinema play demo.cast

# Convert to shareable format
asciinema convert -f asciicast-v2 demo.cast demo-v2.cast
agg --font-family "MesloLGS Nerd Font Mono" demo-v2.cast demo.gif
ffmpeg -i demo.gif -movflags +faststart -pix_fmt yuv420p demo.mp4

# NEVER upload to asciinema.org
# Share MP4 locally via GitHub PR comments or internal channels
```