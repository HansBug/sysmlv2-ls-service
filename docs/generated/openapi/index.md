## Generated endpoint summary

Generated from `openapi/service.v1.yaml`. Regenerate this section with `pnpm run docs:generate:openapi` after changing the OpenAPI document.

| Method | Path | Operation | Summary | Responses |
| --- | --- | --- | --- | --- |
| `GET` | `/healthz` | `getHealth` | Check service liveness. | 200 |
| `GET` | `/v1/capabilities` | `getCapabilities` | Show supported language-service capabilities and effective limits. | 200 |
| `GET` | `/v1/version` | `getVersion` | Show service, upstream, and build version metadata. | 200 |
| `POST` | `/v1/validate` | `validateSysML` | Validate one request-local SysML/KerML workspace. | 200, 400, 413, 503 |

## Generated schema index

| Schema | Type | Properties | Required fields |
| --- | --- | --- | --- |
| `CapabilitiesResponse` | object | 4 | `languages`, `validationChecks`, `standardLibrary`, `limits` |
| `ErrorResponse` | object | 3 | `error`, `message` |
| `FileValidationSummary` | object | 5 | `uri`, `language`, `parserErrors`, `lexerErrors`, `diagnostics` |
| `HealthResponse` | object | 3 | `ok`, `service`, `version` |
| `HttpLimits` | object | 1 | `bodyLimitBytes` |
| `ServiceDiagnostic` | object | 6 | `severity`, `source`, `message`, `uri`, `range` |
| `SourcePosition` | object | 2 | `line`, `character` |
| `SourceRange` | object | 2 | `start`, `end` |
| `SysMLFileInput` | object | 4 | `text` |
| `ValidateLimits` | object | 4 | `maxFiles`, `maxFileTextBytes`, `maxTotalTextBytes`, `validationTimeoutMs` |
| `ValidateMeta` | object | 3 | `standardLibrary`, `validationChecks`, `elapsedMs` |
| `ValidateRequest` | object | 3 | `files` |
| `ValidateResponse` | object | 4 | `ok`, `diagnostics`, `files`, `meta` |
| `VersionResponse` | object | 3 | `service`, `upstream`, `build` |
