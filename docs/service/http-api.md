# HTTP API

The generated OpenAPI summary is available in [the OpenAPI reference](../reference/openapi.md). The canonical machine-readable document is `openapi/service.v1.yaml`.

HTTP errors such as schema failures, payload limits, timeouts, and internal service errors are service errors. They are not returned as SysML diagnostics. SysML diagnostics appear only in successful `POST /v1/validate` responses.
