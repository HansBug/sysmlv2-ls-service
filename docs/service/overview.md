# Service overview

The service exposes the pinned upstream `sysml-2ls` language-server core through a stable HTTP boundary. Public responses are service-owned DTOs from `src/contracts.ts`; raw Langium documents and upstream object shapes are not part of the API contract.

Current endpoints:

- `GET /healthz`
- `GET /v1/capabilities`
- `GET /v1/version`
- `POST /v1/validate`

A validation request builds one request-local workspace. Imports can resolve among files submitted in the same request, and requests remain isolated from each other.
