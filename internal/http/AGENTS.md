# internal/http

Use net/http and httptest. Bound and validate bodies, propagate request context, map service errors to safe statuses, set server timeouts. Handlers call services, never concrete storage.
