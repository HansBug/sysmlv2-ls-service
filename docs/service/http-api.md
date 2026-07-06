# HTTP API

The canonical machine-readable contract is `openapi/service.v1.yaml`; the generated summary is in the [OpenAPI reference](../reference/openapi.md). This page explains the same API from an operational caller perspective.

## Health

```http
GET /healthz
```

Successful response:

```json
{
  "ok": true,
  "service": "sysmlv2-ls-service",
  "version": "0.1.0"
}
```

Use this endpoint for container liveness and quick smoke checks. It does not validate upstream functionality.

## Capabilities

```http
GET /v1/capabilities
```

Successful response shape:

```json
{
  "languages": [
    { "id": "sysml", "extensions": [".sysml"] },
    { "id": "kerml", "extensions": [".kerml"] }
  ],
  "validationChecks": ["all", "none"],
  "standardLibrary": ["none"],
  "limits": {
    "validate": {
      "maxFiles": 64,
      "maxFileTextBytes": 524288,
      "maxTotalTextBytes": 1048576,
      "validationTimeoutMs": 30000
    },
    "http": {
      "bodyLimitBytes": 5242880
    }
  }
}
```

The Python client uses this endpoint for automatic client-side limit preflight. A disabled limit appears as JSON `null`.

## Version

```http
GET /v1/version
```

This endpoint reports service version, service revision, upstream package version, upstream submodule revision, build date, and Node.js runtime. See [Versioning](versioning.md) for precedence and Docker stamping.

## Validate

```http
POST /v1/validate
content-type: application/json
```

Minimal request:

```json
{
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "text": "package Demo { part def Vehicle; }"
    }
  ],
  "standardLibrary": "none",
  "validationChecks": "all"
}
```

Multi-file request:

```json
{
  "files": [
    {
      "uri": "memory:///library.sysml",
      "text": "package Library { part def Vehicle; }"
    },
    {
      "uri": "memory:///model.sysml",
      "text": "package Model { public import Library::*; part car : Vehicle; }"
    }
  ]
}
```

Successful HTTP response with validation success:

```json
{
  "ok": true,
  "diagnostics": [],
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "language": "sysml",
      "parserErrors": 0,
      "lexerErrors": 0,
      "diagnostics": 0
    }
  ],
  "meta": {
    "standardLibrary": "none",
    "validationChecks": "all",
    "elapsedMs": 12.34
  }
}
```

Validation failures still use HTTP `200` when the request is well-formed. In that case `ok` is `false` and `diagnostics` contains parser/linking/semantic diagnostics.

## Service errors versus SysML diagnostics

| Condition                                           | HTTP status | Error code           | Returned as diagnostic? |
| --------------------------------------------------- | ----------- | -------------------- | ----------------------- |
| Schema validation failure                           | `400`       | `bad_request`        | No                      |
| Duplicate explicit URI/path before canonicalization | `400`       | `bad_request`        | No                      |
| Duplicate canonical URI after URI conversion        | `400`       | `bad_request`        | No                      |
| HTTP body exceeds body limit                        | `413`       | `payload_too_large`  | No                      |
| Validation timeout                                  | `503`       | `validation_timeout` | No                      |
| Unexpected server exception                         | `500`       | `internal_error`     | No                      |
| SysML parser/linking/semantic problem               | `200`       | n/a                  | Yes                     |

5xx responses deliberately avoid exposing internal exception messages.

## Curl recipes

Validate and show only diagnostics:

```bash
curl -sS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///broken.sysml","text":"package Broken { part def }"}]}' \
  | jq '.ok, .diagnostics'
```

Skip semantic checks while keeping lexer/parser diagnostics:

```bash
curl -sS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data @- <<'JSON' | jq '.meta, .diagnostics'
{
  "validationChecks": "none",
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "text": "package Demo { part def Vehicle; }"
    }
  ]
}
JSON
```
