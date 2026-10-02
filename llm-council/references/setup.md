# Guided setup

Run the setup diagnostic first. The runner requires macOS or Linux because it uses POSIX process groups. Check Python 3.11+, executable discovery, and the installed CLI's `--help` before changing anything. Confirm the intended account and provider with the user. Do not print API keys or copy authentication files.

Use official installation and authentication instructions for the current platform:

- Claude Code: https://code.claude.com/docs/en/setup and https://code.claude.com/docs/en/cli-reference
- Codex CLI: https://developers.openai.com/codex/cli and https://developers.openai.com/codex/cli/reference
- Cursor Agent: https://cursor.com/docs/cli/installation and https://cursor.com/docs/cli/reference/parameters

If installation is needed, have the current LLM guide or run the official installation within the user's authorization. Inspect any downloaded installer before executing it. Authentication that requires browser interaction remains with the user. Never bypass permissions, silently expand grants, or retry a model call through another service.

Guide the user to choose default members and scope. Write the documented JSON to the repository root for shared defaults, or the user config directory for personal defaults. Do not put secrets in these files. Preserve unrelated configuration. For session-only choices use `members --session` instead.

Run `--dry-run` to check flags before a small real review. Distinguish executable present, authenticated, and successfully reviewed. A setup report proves only installation and config parsing. Older CLI versions may need an update to support the runner's permission controls. Do not drop those controls to make an old version work.

Install all three sibling skill folders (`llm-council`, `llm-council-setup`, `llm-council-members`) into the harness's supported skills directory. The setup and members entries use portable hyphenated skill names. The user may request `llm-council:setup` or `llm-council:members` in natural language, and the base skill routes those requests. Exact colon slash commands require harness-specific command packaging and are not claimed by these standalone Agent Skills folders.

Cursor temporary permission controls follow https://prod.cursor.com/docs/cli/reference/permissions and https://prod.cursor.com/docs/cli/reference/configuration. Deny takes precedence over inherited allow rules. This config lives only in the runner workspace and does not alter user preferences.

Redaction markers in known provider authentication environment variables stop that member before it launches. Report variable names only, obtain real values privately, and do not rotate credentials or expand grants to compensate.

## Troubleshooting a member that times out

Retry that member alone on a one-line prompt before blaming the packet. If a trivial prompt also times out, the CLI is stuck before the model call, not in it.

The timeout error names the executables still running. A shell there (`zsh`, `bash`, `sh`) means the CLI was stuck in shell startup. cursor-agent snapshots `$SHELL -ilc` before answering. The runner points Cursor at `/bin/sh`, but other wrappers may not, and one dotfile that blocks without a terminal stalls every such run. On macOS, Homebrew bash 5.3 before patch 016 deadlocks writing a heredoc of 512 bytes or more into a pipe while system pipe memory is short. `pyenv virtualenv-init` in a zsh startup file hits that path. Check with `bash --version`, upgrade to 5.3.16 or later, and kill any processes left hung by earlier runs.

Cursor also starts every MCP server already approved in the user's Cursor config, even though the runner denies MCP calls. Expect tens of seconds of extra startup when those servers are fetched on demand, for example through `bunx` or `npx`. Review `cursor-agent mcp list` with the user. Server command lines are visible to other local processes, so keep credentials out of server arguments.
