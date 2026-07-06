# OpenAPI

The canonical OpenAPI document is `openapi/service.v1.yaml`. It is linted by `pnpm run openapi:check` and drift-tested against route behavior.

Use this page when you want a quick human-readable endpoint and schema index. Use the YAML file directly when generating clients or validating requests in external tooling.

## Caller rules captured by the spec

- The public API is JSON-only for current endpoints.
- `POST /v1/validate` accepts one request-local workspace containing one or more files.
- `standardLibrary` currently supports only `none`.
- `validationChecks` supports `all` and `none`.
- Service errors use `ErrorResponse`; SysML diagnostics are returned only inside successful validate responses.

## Generated summary

--8<-- "docs/generated/openapi/index.md"

## Validation request example

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

## Error response example

```json
{
  "error": "bad_request",
  "message": "Request body failed schema validation.",
  "issues": []
}
```
