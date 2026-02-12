#!/usr/bin/env bash
set -euo pipefail

cat <<'TEMPLATE'
# PR description update (avoids literal \n)
cat > /tmp/pr-body.md <<'PR_BODY'
## Summary

TODO

## Changes

| Area | Change | Why |
| ---- | ------ | --- |
| TODO | TODO   | TODO |
PR_BODY

gh pr edit <PR_NUMBER> --body-file /tmp/pr-body.md

# PR comment (avoids literal \n)
cat > /tmp/pr-comment.md <<'PR_COMMENT'
Please review the retry flow in
[`client.py#L42-L98`](https://github.com/myorg/myrepo/blob/<sha>/path/client.py#L42-L98).
<!-- permalink-meta: branch=<branch>, timestamp=<ISO8601> -->
PR_COMMENT

gh pr comment <PR_NUMBER> --body-file /tmp/pr-comment.md
TEMPLATE
