# Onboarding and delivery

Install Go 1.27.1, Node 22, Python 3.11 or later, Git and optionally pre-commit.
Clone this repository, check out `v2`, and run `go mod download` and
`node scripts/verify.mjs`. Enable pre-commit with `pre-commit install` if installed.
There are no third-party Go modules initially. The race detector needs a C compiler.

Create ticket worktrees with `git worktree add -b feat/BAC-123 ../go-BAC-123 v2`.
The vendor tree and skills are tracked files and remain present in every worktree.
Use Backend (`BAC`) issues. Read shared delivery-review doctrine; report gate evidence,
remaining limitations and the PR URL. PRs target `v2`; never push authored edits to `main`.
Do not change tests and application behavior without tracing the requested requirement.

<!-- harness:agnostic -->
To refresh layer A, clone jchen1707/harness on `v2` with full history and a clean checkout.
Run `python3 /path/to/harness/scripts/vendor_sync.py sync --harness /path/to/harness --target .`,
then its `check` command with the same arguments. Commit the manifest and discovery stubs.
To inspect generated output, run `python3 .agents/transform/generate_main.py . /tmp/go-main`.
The generation workflow checks the artifact before publishing with an explicit lease.
Publishing needs WORKFLOW_PAT with repository and workflow-write permission, supplied via
GitHub's encrypted Actions secrets. PR checks use their ordinary read-only token.
<!-- /harness:agnostic -->
<!-- harness:claude
Register `/plugin marketplace add jchen1707/harness` before starting Claude Code. The enabled plugin supplies shared hooks, skills and review frames. For terminal verification and pre-commit, export CLAUDE_PLUGIN_ROOT to the installed plugin directory. `claude --bare` skips that enforcement. Pin the marketplace entry if updates must be deliberate.
/harness:claude -->
