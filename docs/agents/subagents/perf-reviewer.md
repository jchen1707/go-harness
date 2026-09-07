# perf-reviewer — Go checklist

Read docs/architecture.md as authority. Combine this checklist with the shared frame.

Check bounded goroutines and queues, HTTP connection reuse, body buffering and hot-path allocations. Require measurements for optimization claims and deadlines for I/O.
