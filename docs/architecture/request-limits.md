# Request-limit architecture

Request limits are resolved once when the Fastify application is built, then injected into request schemas and route behavior.

## Implementation map

| File               | Responsibility                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| `src/limits.ts`    | Defaults, environment parsing, disable syntax, Fastify body-limit conversion.                          |
| `src/contracts.ts` | Per-request file count and text byte schema validation.                                                |
| `src/app.ts`       | Fastify `bodyLimit`, duplicate canonical URI rejection, timeout wrapper, `/v1/capabilities` reporting. |
| Python client      | Optional client-side preflight based on `/v1/capabilities`.                                            |

## Disabled limit representation

`src/limits.ts` represents a disabled guard as `null`. This maps directly to JSON `null` in `/v1/capabilities` and to "skip this check" in schema/route code.

```ts
const limits = resolveServiceLimits({ VALIDATE_MAX_FILES: "0" });
// limits.validate.maxFiles === null
```

## Startup validation

Environment variables must be positive integers or one of `0`, `none`, or `unlimited`. Invalid values throw during service construction, so a bad Docker environment fails early rather than silently using surprising defaults.

## Timeout behavior

The validation timeout wraps the adapter promise and returns HTTP `503 validation_timeout` when it fires. Disabling the timeout removes this service-owned wrapper but does not cancel or bound upstream work by itself.

## Design rationale

The limits are configurable because deployment environments differ. A local research workflow may need larger multi-file requests; a public service may need stricter guardrails. Keeping the limits service-owned and reported through `/v1/capabilities` lets clients adapt without assuming hard-coded defaults.
