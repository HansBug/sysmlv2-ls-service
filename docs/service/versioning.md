# Versioning

`VERSION` is the canonical service version and must match `package.json.version`. `GET /v1/version` reports service version, service revision, upstream package version, upstream submodule revision, build date, and Node.js runtime.

Service version precedence is:

1. `SERVICE_VERSION` environment override.
2. `VERSION` file.
3. `package.json.version`.
4. `0.0.0` fallback.

Release tags must equal `v$(cat VERSION)`.
