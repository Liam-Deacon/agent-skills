# Examples

## Issue Description Skeleton

~~~markdown
## Problem

Retries do not apply jitter and spike backend error rates [1].

## Proposed Change

| Area        | Change               | Benefit                |
| ----------- | -------------------- | ---------------------- |
| HTTP client | Add jittered backoff | Reduce coordinated load|
| Worker      | Retry cap at 5       | Bound execution time   |

## Flow

```text
Request -> Client -> Retry Logic -> Upstream Service
```

## Evidence

- See [`client.py#L42-L98`](https://github.com/myorg/myrepo/blob/abc/path/client.py#L42-L98)
<!-- permalink-meta: branch=feature/retry, timestamp=2026-02-12T15:20:00Z -->

## References

[1]: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
~~~
