# Compatibility

Go is pinned in go.mod and .go-version; CI reads .go-version. Node 22 runs shared hooks;
Python 3.11+ runs the unchanged upstream branch generator and harness tests.
macOS and Linux are supported; race tests need a C compiler. Windows hook adapters are
provided but this repository does not claim Windows CI coverage.

The harness has no application startup command, database or AI/MCP dependencies.
Consumers own their module path, deployment configuration and dependency choices.
