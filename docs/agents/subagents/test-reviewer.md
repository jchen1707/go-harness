# test-reviewer — Go checklist

Read docs/architecture.md as authority. Combine this checklist with the shared frame.

Require observable behavior tests with testing and httptest, including cancellation, deadlines, failures and graceful shutdown. Race detection does not replace concurrency assertions. Avoid timing sleeps and internal mocks.
