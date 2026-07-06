# Python reference

This page is a browser-friendly reference for the installable `sysmlv2slclient` package. The source package still carries full reStructuredText docstrings and those docstrings are checked by `python scripts/check-python-docs.py`; this page keeps the rendered site compact and readable.

## Package roadmap

| Export family    | Primary objects                                                               | Purpose                                                            |
| ---------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Client           | `SysMLV2LSClient`                                                             | Calls health, capabilities, version, and validation endpoints.     |
| Request DTOs     | `SysMLFile`                                                                   | Represents submitted SysML/KerML documents.                        |
| Response DTOs    | `HealthResponse`, `CapabilitiesResponse`, `ValidateResult`, `VersionResponse` | Parse service-owned responses without exposing upstream internals. |
| Diagnostic DTOs  | `Diagnostic`, `SourceRange`, `SourcePosition`                                 | Preserve normalized diagnostic location and metadata.              |
| Limit DTOs       | `ServiceLimits`, `ValidateLimits`, `HttpLimits`                               | Model `/v1/capabilities` effective limits.                         |
| Exceptions       | `SysMLClientError` and subclasses                                             | Stable failure categories for SDK callers and CLI handling.        |
| Directory helper | `collect_directory_files`                                                     | Builds deterministic file DTOs from a root directory.              |

## Version constants

| Name                                      | Meaning                                             |
| ----------------------------------------- | --------------------------------------------------- |
| `sysmlv2slclient.__version__`             | Python client package version.                      |
| `sysmlv2slclient.__service_api_version__` | Service API version targeted by the client package. |

## `SysMLV2LSClient`

```python
SysMLV2LSClient(
    base_url,
    timeout=30.0,
    user_agent=None,
    session=None,
    enforce_client_limits=True,
    limits="auto",
)
```

| Constructor argument    | Type                                   | Description                                                                                                                 |
| ----------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `base_url`              | `str`                                  | Service root URL with scheme and host. Query strings and fragments are rejected. Reverse-proxy path prefixes are preserved. |
| `timeout`               | `float`                                | HTTP timeout passed to `requests`.                                                                                          |
| `user_agent`            | `str or None`                          | Optional User-Agent. Defaults to `sysmlv2slclient/<version>`.                                                               |
| `session`               | `requests.Session or None`             | Optional session-compatible object for pooling or tests.                                                                    |
| `enforce_client_limits` | `bool`                                 | Enables client-side preflight against known service limits.                                                                 |
| `limits`                | `"auto", None, ServiceLimits, or dict` | `"auto"` fetches `/v1/capabilities`; `None` skips known client-side limit checks.                                           |

### Endpoint methods

| Method                 | Signature                                                                                                                                                                                                                                      | Return type            | Notes                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------------- |
| `health`               | `health()`                                                                                                                                                                                                                                     | `HealthResponse`       | Calls `GET /healthz`.                                               |
| `capabilities`         | `capabilities()`                                                                                                                                                                                                                               | `CapabilitiesResponse` | Calls `GET /v1/capabilities` and refreshes cached automatic limits. |
| `refresh_capabilities` | `refresh_capabilities()`                                                                                                                                                                                                                       | `CapabilitiesResponse` | Explicit alias for refreshing capabilities.                         |
| `version`              | `version()`                                                                                                                                                                                                                                    | `VersionResponse`      | Calls `GET /v1/version`.                                            |
| `validate`             | `validate(files, standard_library="none", validation_checks="all")`                                                                                                                                                                            | `ValidateResult`       | Low-level validation from `SysMLFile` objects or equivalent dicts.  |
| `validate_files`       | `validate_files(files, standard_library="none", validation_checks="all")`                                                                                                                                                                      | `ValidateResult`       | Readable alias for explicit multi-file DTOs.                        |
| `validate_text`        | `validate_text(text, uri=None, path=None, language=None, standard_library="none", validation_checks="all")`                                                                                                                                    | `ValidateResult`       | Single in-memory text document.                                     |
| `validate_directory`   | `validate_directory(path, include=("**/*.sysml",), exclude=None, uri_scheme="memory", relative_uris=True, language=None, encoding="utf-8", encoding_errors="strict", follow_symlinks=False, standard_library="none", validation_checks="all")` | `ValidateResult`       | Collects files under a root and validates them together.            |

### Client examples

```python
from sysmlv2slclient import SysMLFile, SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")

single = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)

multi = client.validate_files(
    [
        SysMLFile("package Library { part def Vehicle; }", uri="memory:///library.sysml"),
        SysMLFile(
            "package Model { public import Library::*; part car : Vehicle; }",
            uri="memory:///model.sysml",
        ),
    ]
)

workspace = client.validate_directory(
    "models",
    include=("**/*.sysml", "**/*.kerml"),
    exclude=("vendor/**",),
)
```

## Request model

### `SysMLFile`

```python
SysMLFile(text, uri=None, path=None, language=None)
```

| Field      | Type                        | Description                                                                          |
| ---------- | --------------------------- | ------------------------------------------------------------------------------------ |
| `text`     | `str`                       | SysML/KerML document text sent to the service.                                       |
| `uri`      | `str or None`               | Optional request-local URI; mutually exclusive with `path`.                          |
| `path`     | `str or None`               | Optional path converted by the service to a file URI; mutually exclusive with `uri`. |
| `language` | `"sysml", "kerml", or None` | Optional explicit language.                                                          |

Methods:

| Method                      | Purpose                                                    |
| --------------------------- | ---------------------------------------------------------- |
| `SysMLFile.from_dict(data)` | Parse a request file DTO from a dictionary.                |
| `to_dict()`                 | Convert to the JSON shape accepted by `POST /v1/validate`. |

## Validation response model

### `ValidateResult`

| Field         | Type                          | Description                                                         |
| ------------- | ----------------------------- | ------------------------------------------------------------------- |
| `ok`          | `bool`                        | False when parser/lexer errors or error-severity diagnostics exist. |
| `diagnostics` | `list[Diagnostic]`            | Normalized diagnostics from Langium/upstream.                       |
| `files`       | `list[FileValidationSummary]` | Per-file summary rows.                                              |
| `meta`        | `ValidateMeta`                | Validation options and elapsed time.                                |
| `raw`         | `dict`                        | Original parsed response dictionary.                                |

Methods:

| Method                           | Purpose                                              |
| -------------------------------- | ---------------------------------------------------- |
| `ValidateResult.from_dict(data)` | Parse a validation response DTO.                     |
| `to_dict()`                      | Convert the response back to JSON-serializable data. |
| `raise_for_diagnostics()`        | Raise `SysMLDiagnosticsError` when `ok` is false.    |

### `Diagnostic`

| Field      | Type                | Description                                   |
| ---------- | ------------------- | --------------------------------------------- |
| `severity` | `str`               | `error`, `warning`, `information`, or `hint`. |
| `source`   | `str`               | Diagnostic source, usually `sysml-2ls`.       |
| `message`  | `str`               | Human-readable diagnostic message.            |
| `uri`      | `str`               | Document URI associated with the diagnostic.  |
| `range`    | `SourceRange`       | Zero-based source range.                      |
| `code`     | `str, int, or None` | Upstream/Langium diagnostic code.             |
| `raw`      | `dict`              | Original diagnostic object.                   |

### Source locations and summaries

| Class                   | Fields                                                                   | Purpose                     |
| ----------------------- | ------------------------------------------------------------------------ | --------------------------- |
| `SourcePosition`        | `line`, `character`                                                      | Zero-based source position. |
| `SourceRange`           | `start`, `end`                                                           | Diagnostic source range.    |
| `FileValidationSummary` | `uri`, `language`, `parser_errors`, `lexer_errors`, `diagnostics`, `raw` | Per-file response summary.  |
| `ValidateMeta`          | `standard_library`, `validation_checks`, `elapsed_ms`, `raw`             | Validate response metadata. |

All DTO classes provide `from_dict(...)` and `to_dict()` helpers where relevant.

## Metadata response models

| Class                  | Fields                                                                                     | Endpoint                     |
| ---------------------- | ------------------------------------------------------------------------------------------ | ---------------------------- |
| `HealthResponse`       | `ok`, `service`, `version`, `raw`                                                          | `/healthz`                   |
| `LanguageInfo`         | `id`, `extensions`, `raw`                                                                  | nested in `/v1/capabilities` |
| `ValidateLimits`       | `max_files`, `max_file_text_bytes`, `max_total_text_bytes`, `validation_timeout_ms`, `raw` | nested in `/v1/capabilities` |
| `HttpLimits`           | `body_limit_bytes`, `raw`                                                                  | nested in `/v1/capabilities` |
| `ServiceLimits`        | `validate`, `http`, `raw`                                                                  | nested in `/v1/capabilities` |
| `CapabilitiesResponse` | `languages`, `validation_checks`, `standard_library`, `limits`, `raw`                      | `/v1/capabilities`           |
| `ServiceVersionInfo`   | `name`, `version`, `revision`, `source_repository`, `raw`                                  | nested in `/v1/version`      |
| `UpstreamSysML2LSInfo` | `version`, `revision`, `package_name`, `repository`, `raw`                                 | nested in `/v1/version`      |
| `UpstreamInfo`         | `sysml2ls`, `raw`                                                                          | nested in `/v1/version`      |
| `BuildInfo`            | `date`, `node_version`, `raw`                                                              | nested in `/v1/version`      |
| `VersionResponse`      | `service`, `upstream`, `build`, `raw`                                                      | `/v1/version`                |

## Directory helper

```python
collect_directory_files(
    path,
    include=("**/*.sysml",),
    exclude=None,
    uri_scheme="memory",
    relative_uris=True,
    language=None,
    encoding="utf-8",
    encoding_errors="strict",
    follow_symlinks=False,
)
```

| Option                         | Behavior                                                                          |
| ------------------------------ | --------------------------------------------------------------------------------- |
| `path`                         | Directory root. All collected files must remain inside this root.                 |
| `include`                      | Relative glob pattern(s) or callable. Default includes recursive `.sysml` files.  |
| `exclude`                      | Relative glob pattern(s) or callable to skip files.                               |
| `uri_scheme`                   | `"memory"` for generated `memory:///` URIs or `"file"` for absolute file paths.   |
| `relative_uris`                | In memory mode, use root-relative URIs when true.                                 |
| `language`                     | Optional explicit language for all collected files.                               |
| `encoding` / `encoding_errors` | File decoding controls.                                                           |
| `follow_symlinks`              | Follow only symlinks that remain inside the root; loops and escapes are rejected. |

## Exception hierarchy

| Exception                   | Meaning                                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `SysMLClientError`          | Base class for SDK failures.                                                                                   |
| `SysMLConnectionError`      | Network, DNS, timeout, refused connection, or transport error from `requests`.                                 |
| `SysMLServiceError`         | HTTP error response from the service. Carries status code, error code, message, optional issues, and raw body. |
| `SysMLResponseError`        | Response JSON or DTO shape is malformed.                                                                       |
| `SysMLDiagnosticsError`     | Raised by `ValidateResult.raise_for_diagnostics()`.                                                            |
| `SysMLDirectoryError`       | Directory collection, glob, symlink, or decoding failure.                                                      |
| `SysMLValidationLimitError` | Client-side request preflight exceeded known service limits.                                                   |

## CLI reference

The Click CLI exposes the same main operations. See the generated [CLI reference](../../generated/cli/index.md) for current `sysmlv2sl --help` output and subcommand help.
