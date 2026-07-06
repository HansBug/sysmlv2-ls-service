# Docker

Docker is the recommended runtime path for callers that want a reproducible Node.js 24 service image without installing the upstream language-server packages locally.

## Published images

```bash
docker run --rm -p 3000:3000 ghcr.io/hansbug/sysmlv2-ls-service:0.1.0
```

Docker Hub publishes the same service under the configured namespace:

```bash
docker run --rm -p 3000:3000 hansbug/sysmlv2-ls-service:0.1.0
```

Release tags include `vX.Y.Z`, `X.Y.Z`, `latest`, and `sha-<short-commit>` for successful release builds. Prefer an immutable version or SHA tag for production deployments.

## Build locally

```bash
docker build -t sysmlv2-ls-service:local .
docker run --rm -p 3000:3000 sysmlv2-ls-service:local
```

For release-equivalent provenance metadata, stamp the image with build args:

```bash
UPSTREAM_SYSML_2LS_VERSION="$(
  node -p 'require("./upstream/sysml-2ls/packages/syside-languageserver/package.json").version'
)"
docker build -t sysmlv2-ls-service:local \
  --build-arg SERVICE_VERSION="$(cat VERSION)" \
  --build-arg SERVICE_REVISION="$(git rev-parse HEAD)" \
  --build-arg SOURCE_REPOSITORY=https://github.com/HansBug/sysmlv2-ls-service \
  --build-arg UPSTREAM_SYSML_2LS_VERSION="$UPSTREAM_SYSML_2LS_VERSION" \
  --build-arg UPSTREAM_SYSML_2LS_REVISION="$(git -C upstream/sysml-2ls rev-parse HEAD)" \
  --build-arg UPSTREAM_SYSML_2LS_REPOSITORY=https://github.com/sensmetry/sysml-2ls \
  --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  .
```

## Smoke checks

```bash
curl -fsS http://127.0.0.1:3000/healthz
curl -fsS http://127.0.0.1:3000/v1/version | jq
curl -fsS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///demo.sysml","text":"package Demo { part def Vehicle; }"}]}' \
  | jq '.ok'
```

A healthy container returns `true` for the final command and `/v1/version` should report a Node.js runtime beginning with `v24.` for published images.

## Configure service-owned limits

The request limits are implemented by this service, not by upstream `sysml-2ls`. They are operational guardrails around file count, text size, body size, and validation wall-clock time. Every limit can be overridden or disabled through environment variables:

| Variable                        | Default   | Disable values           | Effect                                                     |
| ------------------------------- | --------- | ------------------------ | ---------------------------------------------------------- |
| `VALIDATE_MAX_FILES`            | `64`      | `0`, `none`, `unlimited` | Maximum files per validation request.                      |
| `VALIDATE_MAX_FILE_TEXT_BYTES`  | `524288`  | `0`, `none`, `unlimited` | Maximum UTF-8 text bytes for one submitted file.           |
| `VALIDATE_MAX_TOTAL_TEXT_BYTES` | `1048576` | `0`, `none`, `unlimited` | Maximum total UTF-8 text bytes across all submitted files. |
| `HTTP_BODY_LIMIT_BYTES`         | `5242880` | `0`, `none`, `unlimited` | Fastify request body cap.                                  |
| `VALIDATION_TIMEOUT_MS`         | `30000`   | `0`, `none`, `unlimited` | Service timeout wrapper around validation.                 |

Example with all service-owned guards disabled:

```bash
docker run --rm -p 3000:3000 \
  -e VALIDATE_MAX_FILES=0 \
  -e VALIDATE_MAX_FILE_TEXT_BYTES=0 \
  -e VALIDATE_MAX_TOTAL_TEXT_BYTES=0 \
  -e HTTP_BODY_LIMIT_BYTES=0 \
  -e VALIDATION_TIMEOUT_MS=0 \
  ghcr.io/hansbug/sysmlv2-ls-service:0.1.0
```

!!! warning "Disabling limits is not infinite capacity"

    A disabled service limit is reported as JSON `null` from `/v1/capabilities`, but Node.js, Fastify/Node parsers, container memory, the upstream validator, and the operating system still impose real limits. Disable guards only for trusted workloads with external resource controls.

## Port and process notes

- The image listens on `PORT` if set, otherwise `3000`.
- The runtime image uses the `node` user.
- If host port `3000` is occupied, map a different port such as `-p 13000:3000` and use `http://127.0.0.1:13000` from clients.
