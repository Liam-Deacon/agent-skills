# Configuration

Both config files use JSON with these fields. Unknown fields, invalid types, malformed JSON and invalid selectors stop the run. Bare model selectors bind to the default harness explicitly declared in their own config layer, or built-in Codex when that layer omits it. Changing the repository default harness does not redirect inherited user members. Repository configuration cannot provide executable paths, shell commands, hooks or extra CLI flags.

```json
{
  "version": 1,
  "members": ["claude:default@default", "codex:default@default", "cursor:default@default"],
  "default_harness": "codex",
  "timeout_seconds": 240,
  "concurrency": 3,
  "max_output_chars": 100000
}
```

A repository config at the Git root overrides matching fields in the user config. Without Git, the current working directory is the root. An invalid higher-precedence file does not silently fall back. Explicit run members override session members, which override configured members. Each run needs 1 to 8 members. Timeout is per member, 10 to 1800 seconds. Concurrency is 1 to 8. Stdout is bounded per member by max_output_chars after decoding, with an initial byte cap of four times that value. Stderr capture has a separate fixed 1 MB cap. Further stderr is drained and discarded, and stderr_truncated marks the result, without discarding a valid answer. No prompt or result caching is enabled.

The selector grammar is `[harness:]model[@effort]`. A bare harness means its default model. Model identifiers use letters, numbers, periods, underscores, slashes, pluses and hyphens. Bracket parameters and executable flags are not accepted. A model unsupported by the provider fails visibly rather than falling back silently.

Effort is provider-specific. Claude passes `--effort`, Codex passes `model_reasoning_effort`, Cursor adds `[effort=...]` to its explicit model selector. Cursor cannot override effort for `default` because its CLI needs an explicit parameterized model. Valid strings are checked, but whether a particular model supports them is determined by the CLI and provider. `default` always omits the override.

Session members live under `$XDG_STATE_HOME/llm-council` or `~/.local/state/llm-council`. The file uses a hash of the caller's explicit session ID, is atomically written with owner-only permissions and stores only member selectors. Use a different ID for independent sessions. Remove that session file to return to configured defaults.
