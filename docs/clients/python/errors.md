# Python errors

The Python SDK maps transport, service, malformed-response, validation-diagnostic, directory, and client-limit failures into a stable exception hierarchy. Validation diagnostics are not raised by default; they are returned in `ValidateResult` unless caller code asks to raise them.

## Exception hierarchy

| Exception                   | Typical source                        | Notes                                                                            |
| --------------------------- | ------------------------------------- | -------------------------------------------------------------------------------- |
| `SysMLClientError`          | Base class                            | Catch this for all SDK-level failures.                                           |
| `SysMLConnectionError`      | `requests` transport failure          | DNS, refused connection, timeout, TLS, or other local transport errors.          |
| `SysMLServiceError`         | HTTP status `>=400` from the service  | Carries status code, service error code, message, optional issues, and raw body. |
| `SysMLResponseError`        | Malformed or unexpected response JSON | Raised when JSON parsing or DTO parsing fails.                                   |
| `SysMLDiagnosticsError`     | Caller-invoked diagnostic raising     | Wraps diagnostics from a `ValidateResult`.                                       |
| `SysMLDirectoryError`       | Directory collection failure          | Invalid root, unsafe glob, symlink escape/loop, or file decoding failure.        |
| `SysMLValidationLimitError` | Client-side limit preflight           | Request would exceed known service-owned limits.                                 |

## Handling service errors

```python
from sysmlv2slclient import SysMLServiceError, SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
try:
    client.validate_files([])
except SysMLServiceError as error:
    print(error.status_code, error.error, error.message)
```

Most malformed requests are caught client-side before the HTTP call, but server-side schema failures still raise `SysMLServiceError` when returned by the service.

## Handling diagnostics explicitly

```python
from sysmlv2slclient import SysMLDiagnosticsError, SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text("package Broken { part def }")
try:
    result.raise_for_diagnostics()
except SysMLDiagnosticsError as error:
    for diagnostic in error.diagnostics:
        print(diagnostic.code, diagnostic.message)
```

Use this pattern when application code wants validation failure to follow exception-based control flow.

## CLI mapping

The CLI converts SDK/runtime exceptions into exit code `3`. Validation diagnostics with `ok=false` produce exit code `1` instead, because the HTTP request itself succeeded.
