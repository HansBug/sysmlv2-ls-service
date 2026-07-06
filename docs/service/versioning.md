# Versioning

`GET /v1/version` reports service, upstream, build, and runtime provenance. Release and Docker smoke checks should verify this endpoint before declaring an image usable.

## Service version source of truth

`VERSION` is canonical and must match `package.json.version` exactly. The check is:

```bash
pnpm run version:check
```

When bumping the service version:

1. Update `VERSION`.
2. Update `package.json.version` to the same value.
3. Run `pnpm run version:check`.
4. Update docs/examples only when they intentionally name the new release.
5. Use a Git tag exactly equal to `v$(cat VERSION)`.

## `/v1/version` precedence

Service version precedence is:

1. `SERVICE_VERSION` environment override.
2. Root `VERSION` file.
3. `package.json.version`.
4. `0.0.0` fallback.

Unknown placeholder values such as `unknown` are treated as unset by the metadata layer.

## Response fields

```json
{
  "service": {
    "name": "sysmlv2-ls-service",
    "version": "0.1.0",
    "revision": "unknown",
    "sourceRepository": "https://github.com/HansBug/sysmlv2-ls-service"
  },
  "upstream": {
    "sysml2ls": {
      "version": "0.9.1",
      "revision": "unknown",
      "packageName": "syside-languageserver",
      "repository": "https://github.com/sensmetry/sysml-2ls"
    }
  },
  "build": {
    "date": "unknown",
    "nodeVersion": "v24.x.y"
  }
}
```

## Docker stamping

Release images stamp these build args into `/v1/version` and OCI labels:

| Build arg                       | Meaning                                   |
| ------------------------------- | ----------------------------------------- |
| `SERVICE_VERSION`               | Version from `VERSION`.                   |
| `SERVICE_REVISION`              | Service repository commit SHA.            |
| `SOURCE_REPOSITORY`             | Service repository URL.                   |
| `UPSTREAM_SYSML_2LS_VERSION`    | Upstream language-server package version. |
| `UPSTREAM_SYSML_2LS_REVISION`   | Pinned upstream submodule commit.         |
| `UPSTREAM_SYSML_2LS_REPOSITORY` | Upstream repository URL.                  |
| `BUILD_DATE`                    | UTC build timestamp.                      |

If build args are omitted, source and Docker-runtime fallback paths try to recover stable metadata from committed files where possible.

## Tests and docs policy

Tests should read `VERSION`, upstream package metadata, or call `getVersionInfo()` rather than hard-code current versions. Documentation pages that name a published image tag must verify the tag exists before claiming it is available.
