# Docker

Published images are available from GHCR and Docker Hub:

```bash
docker run --rm -p 3000:3000 ghcr.io/hansbug/sysmlv2-ls-service:0.1.0
```

Smoke checks:

```bash
curl -fsS http://127.0.0.1:3000/healthz
curl -fsS http://127.0.0.1:3000/v1/version
```

Request limits are service-owned guards. They can be configured or disabled through environment variables such as `VALIDATE_MAX_FILES=0`, `VALIDATE_MAX_FILE_TEXT_BYTES=0`, `VALIDATE_MAX_TOTAL_TEXT_BYTES=0`, `HTTP_BODY_LIMIT_BYTES=0`, and `VALIDATION_TIMEOUT_MS=0`.
