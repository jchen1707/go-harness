# design-reviewer — Go checklist

Read docs/architecture.md as authority. Combine this checklist with the shared frame.

Check that services own required interfaces, handlers depend on services and adapters stay replaceable. Trace invariants and error ownership across package boundaries.
