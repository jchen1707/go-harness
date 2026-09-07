# go-harness

A standard-library Go harness for backend services and workers. No application is included.
Start with [onboarding](docs/onboarding.md), [architecture](docs/architecture.md) and
[compatibility](docs/compatibility.md). Linear team: Backend (`BAC`).

Use Go 1.27.1, Node 22 and Python 3. Install Go from https://go.dev/dl/.
Run `go mod download`, then `node scripts/verify.mjs`.
The declared gates check formatting without changing files, vet, build, race tests,
and harness infrastructure. Go product templates are outside this repository.

`v2` is authored; `main` is generated for Claude Code. Make changes on a branch from `v2`,
open a PR against `v2`, and let CI regenerate `main` after merge.
