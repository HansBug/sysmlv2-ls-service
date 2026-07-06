# Python reference

This page renders the installable `sysmlv2slclient` package directly from the
client source docstrings. The Python client intentionally uses Sphinx/reStructuredText
field lists, so the MkDocs build config enables the `mkdocstrings` Python
handler's `sphinx` parser. If this page ever shows raw field-list markers, the
docs build is broken.

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

## Client class

::: sysmlv2slclient.client.SysMLV2LSClient

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

## Request and response DTOs

DTO details stay hand-written so the reference remains compact while the core
client and helper APIs above and below are rendered from Sphinx/reStructuredText
docstrings.

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

### Metadata response models

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

::: sysmlv2slclient.directory.collect_directory_files

## Exceptions

| Exception                   | Meaning                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------- |
| `SysMLClientError`          | Base class for SDK failures.                                                                    |
| `SysMLConnectionError`      | Network, DNS, timeout, refused connection, or local transport error from `requests`.            |
| `SysMLServiceError`         | HTTP service error with status code, stable error code, message, optional issues, and raw body. |
| `SysMLResponseError`        | Response JSON or DTO shape is malformed.                                                        |
| `SysMLDiagnosticsError`     | Raised by `ValidateResult.raise_for_diagnostics()` when validation is not `ok`.                 |
| `SysMLDirectoryError`       | Directory collection, glob, symlink, URI, or decoding failure.                                  |
| `SysMLValidationLimitError` | Client-side service-limit preflight failure.                                                    |

## CLI reference

The Click CLI exposes the same main operations. See the generated
[CLI reference](../../generated/cli/index.md) for current `sysmlv2sl --help`
output and subcommand help.
