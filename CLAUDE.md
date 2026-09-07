# go-harness

This is a backend service and worker harness, not an application. Do not invent a server
entry point to make a run command succeed. `cmd/` and `internal/` document future product
boundaries; executable Go initially validates the harness in `tools/harnesscheck/`.

Author only `v2` and feature branches based on it. `main` is generated; never hand-edit it.
Read docs/architecture.md and path-scoped instructions before changing code.
Use linked worktrees per ticket. Linear issues belong to Backend (`BAC`).

The Definition of Done is declared in harness.config.json. Run `node scripts/verify.mjs`
before delivery. Failed or unavailable gates are not a pass. Use the shared gate reporter;
never maintain another selection loop. Review all eight shared axes and concurrency.

Layer A arrives through `harness@harness`. Register `/plugin marketplace add jchen1707/harness` once per machine. Read the plugin's delivery-review and testing doctrine.

Keep secrets out of logs, prompts and commits. See docs/agents/secrets.md.
Delivery instructions and prerequisites are in docs/onboarding.md.
