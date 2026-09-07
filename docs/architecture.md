# Architecture

Use the Go standard library first: net/http at HTTP boundaries, log/slog for structured
logging, testing and net/http/httptest for tests. Add dependencies only for a demonstrated
need. This harness chooses no database, router, queue or deployment platform.

`cmd/<service>/` is the composition root: parse configuration, construct dependencies,
start HTTP servers or workers, then coordinate shutdown. Keep business rules in
`internal/services/`. Services own the small interfaces they consume; storage adapters
implement those interfaces structurally. Inject dependencies explicitly through constructors.
HTTP handlers depend on services. Services do not import HTTP or concrete storage packages.
Configuration is parsed and validated once at startup in `internal/config/` and passed in.
Avoid package globals, init side effects and environment reads spread across the application.

Return errors with operation context using fmt.Errorf and %w; inspect causes with errors.Is
or errors.As. Translate errors to safe HTTP statuses at the boundary. Log once at the owner
of recovery, with slog fields; never log credentials or raw request bodies.

Propagate context.Context as the first argument for cancellable work. Bound outbound I/O
with deadlines and reuse clients. Every goroutine needs an owner, a bound and an exit path.
Limit worker counts and queue sizes, handle backpressure, and synchronize shared state.
The sender owns channel closure. Cancellation must unblock sends and receives.
Use signal.NotifyContext at the composition root, stop admitting work, drain with a bounded
shutdown context, cancel remaining work and wait for goroutines before returning.

HTTP handlers bound request bodies, validate input and content types, and set server read,
write and idle timeouts. Close response bodies; expose safe public errors and enforce
trust boundaries explicitly. No authentication scheme is supplied by this harness.

Tests exercise observable behavior, cancellation, deadlines, error paths and shutdown.
Use table tests when cases share behavior; use httptest at HTTP boundaries. Avoid sleeps
for synchronization and mocks of functions within the same module. Run with the race detector;
a passing race run proves only the paths exercised. Keep implementation absent until a
product requirement calls for it.
