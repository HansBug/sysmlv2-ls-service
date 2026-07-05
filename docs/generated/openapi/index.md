# OpenAPI reference

The canonical OpenAPI document is `openapi/service.v1.yaml`. This generated page summarizes the service-owned HTTP contract; run `pnpm run openapi:check` to lint the spec and detect drift against the implementation.

## Endpoints

| Method | Path | Operation | Summary |
| --- | --- | --- | --- |
| `GET` | `/healthz` | `getHealth` | Check service liveness. |
| `GET` | `/v1/capabilities` | `getCapabilities` | Show supported language-service capabilities and effective limits. |
| `GET` | `/v1/version` | `getVersion` | Show service, upstream, and build version metadata. |
| `POST` | `/v1/validate` | `validateSysML` | Validate one request-local SysML/KerML workspace. |

## Schemas

- `CapabilitiesResponse`
- `ErrorResponse`
- `FileValidationSummary`
- `HealthResponse`
- `HttpLimits`
- `ServiceDiagnostic`
- `SourcePosition`
- `SourceRange`
- `SysMLFileInput`
- `ValidateLimits`
- `ValidateMeta`
- `ValidateRequest`
- `ValidateResponse`
- `VersionResponse`
