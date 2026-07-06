# DTO contracts

The service contract is owned by `src/contracts.ts` and `openapi/service.v1.yaml`. Tests and documentation keep these sources aligned.

## Contract sources

| Source                           | Purpose                                                                  |
| -------------------------------- | ------------------------------------------------------------------------ |
| `src/contracts.ts`               | TypeScript DTO types and Zod request schemas used by the implementation. |
| `openapi/service.v1.yaml`        | Machine-readable API contract for clients and documentation.             |
| `tests/openapi-contract.test.ts` | Drift tests between implementation behavior and OpenAPI expectations.    |
| `docs/reference/openapi.md`      | Human-facing generated summary from the OpenAPI file.                    |

## Contract rules

- Public responses must use service-owned DTOs, never raw upstream objects.
- HTTP request failures use service error responses, not SysML diagnostics.
- Well-formed validation requests return HTTP `200` even when `ok=false` due to diagnostics.
- Unknown diagnostic codes remain visible.
- Warnings do not make `ok=false` by themselves.

## Adding or changing fields

A contract change should update all of the following in one PR:

1. `src/contracts.ts` DTO/schema definitions.
2. Route or adapter behavior in `src/app.ts` / `src/sysml-validator.ts`.
3. OpenAPI schema and examples.
4. Unit/integration tests.
5. Python models/client/CLI when the field is public to SDK users.
6. Documentation pages and generated references.

## Backward-compatibility note

The project is still pre-1.0, but the repository treats public DTO changes as deliberate compatibility events. Avoid exposing temporary upstream implementation details just to make one integration easier.
