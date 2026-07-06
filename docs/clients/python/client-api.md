# Python API

`SysMLV2LSClient` is the class-based SDK wrapper around the current service API. Construct it with the service root URL, then call endpoint methods.

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
print(client.health().ok)
print(client.version().service.version)
```

## Constructor

```python
client = SysMLV2LSClient(
    "http://127.0.0.1:3000",
    timeout=30.0,
    user_agent=None,
    session=None,
    enforce_client_limits=True,
    limits="auto",
)
```

| Argument                | Meaning                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `base_url`              | Service root URL. Scheme and host are required; query strings and fragments are rejected. Reverse-proxy path prefixes are preserved. |
| `timeout`               | `requests` timeout in seconds.                                                                                                       |
| `user_agent`            | Optional custom User-Agent. Defaults to `sysmlv2slclient/<version>`.                                                                 |
| `session`               | Optional `requests.Session`-compatible object for tests or caller-managed pooling.                                                   |
| `enforce_client_limits` | Enables client-side preflight against effective limits.                                                                              |
| `limits`                | `"auto"`, `None`, a `ServiceLimits` object, or equivalent dict.                                                                      |

## Endpoint methods

| Method                          | Service endpoint       | Return type            | Notes                                                             |
| ------------------------------- | ---------------------- | ---------------------- | ----------------------------------------------------------------- |
| `health()`                      | `GET /healthz`         | `HealthResponse`       | Lightweight liveness.                                             |
| `capabilities()`                | `GET /v1/capabilities` | `CapabilitiesResponse` | Refreshes cached automatic limits.                                |
| `refresh_capabilities()`        | `GET /v1/capabilities` | `CapabilitiesResponse` | Alias that makes cache refresh explicit.                          |
| `version()`                     | `GET /v1/version`      | `VersionResponse`      | Client callers can combine this with package `__version__`.       |
| `validate(files, ...)`          | `POST /v1/validate`    | `ValidateResult`       | Low-level workspace validation from `SysMLFile` objects or dicts. |
| `validate_files(files, ...)`    | `POST /v1/validate`    | `ValidateResult`       | Readable alias for explicit file DTOs.                            |
| `validate_text(text, ...)`      | `POST /v1/validate`    | `ValidateResult`       | Single in-memory document.                                        |
| `validate_directory(path, ...)` | `POST /v1/validate`    | `ValidateResult`       | Collect files under a root and validate them together.            |

## Single text validation

```python
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)
print(result.ok)
```

Use `validation_checks="none"` to skip semantic checks while retaining lexer/parser diagnostics:

```python
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
    validation_checks="none",
)
```

## Explicit multi-file workspace

```python
from sysmlv2slclient import SysMLFile

files = [
    SysMLFile(
        text="package Library { part def Vehicle; }",
        uri="memory:///library.sysml",
    ),
    SysMLFile(
        text="package Model { public import Library::*; part car : Vehicle; }",
        uri="memory:///model.sysml",
    ),
]
result = client.validate_files(files)
print(result.ok)
```

All files in the list are submitted as one request-local workspace, so imports can resolve between them.

## Directory validation

```python
result = client.validate_directory(
    "models",
    include=("**/*.sysml", "**/*.kerml"),
    exclude=("vendor/**", "build/**"),
    uri_scheme="memory",
    relative_uris=True,
)
```

Directory collection enforces that include/exclude patterns are relative to the root. Symlinks are skipped by default; `follow_symlinks=True` follows only symlinks that stay inside the root and rejects loops or escapes.

| Option            | Default           | Behavior                                                                  |
| ----------------- | ----------------- | ------------------------------------------------------------------------- |
| `include`         | `("**/*.sysml",)` | Relative glob pattern(s) or callable.                                     |
| `exclude`         | `None`            | Relative glob pattern(s) or callable.                                     |
| `uri_scheme`      | `"memory"`        | `"memory"` creates `memory:///` URIs; `"file"` sends absolute file paths. |
| `relative_uris`   | `True`            | In memory mode, use paths relative to the directory root.                 |
| `language`        | `None`            | Optional explicit `"sysml"` or `"kerml"` for all collected files.         |
| `encoding`        | `"utf-8"`         | File decoding.                                                            |
| `encoding_errors` | `"strict"`        | Python decoding error policy.                                             |
| `follow_symlinks` | `False`           | Follow only safe in-root symlinks when true.                              |

## Diagnostics as data

`ValidateResult.raise_for_diagnostics()` is available when application code wants validation diagnostics to raise, but the default API keeps diagnostics as structured data:

```python
result = client.validate_text("package Broken { part def }")
if not result.ok:
    for diagnostic in result.diagnostics:
        print(diagnostic.code, diagnostic.message)
```

## Reference

The full generated reference is available at [Python reference](../../reference/python/index.md).
