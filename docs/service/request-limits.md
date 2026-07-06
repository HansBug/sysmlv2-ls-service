# Request limits

Request limits are service-owned guardrails implemented in `src/limits.ts`, `src/contracts.ts`, and `src/app.ts`. They are **not** hard-coded upstream `sysml-2ls` limits.

## Defaults and environment variables

| Limit                          | Default              | Environment variable            | Disable values           |
| ------------------------------ | -------------------- | ------------------------------- | ------------------------ |
| Files per validation request   | `64`                 | `VALIDATE_MAX_FILES`            | `0`, `none`, `unlimited` |
| UTF-8 bytes per submitted file | `524288` (`512 KiB`) | `VALIDATE_MAX_FILE_TEXT_BYTES`  | `0`, `none`, `unlimited` |
| Total UTF-8 text bytes         | `1048576` (`1 MiB`)  | `VALIDATE_MAX_TOTAL_TEXT_BYTES` | `0`, `none`, `unlimited` |
| HTTP body bytes                | `5242880` (`5 MiB`)  | `HTTP_BODY_LIMIT_BYTES`         | `0`, `none`, `unlimited` |
| Validation wall-clock timeout  | `30000` ms           | `VALIDATION_TIMEOUT_MS`         | `0`, `none`, `unlimited` |

Positive integers override defaults. Invalid, negative, or non-integer values fail fast during service startup.

## Disable example

```bash
VALIDATE_MAX_FILES=0 \
VALIDATE_MAX_FILE_TEXT_BYTES=0 \
VALIDATE_MAX_TOTAL_TEXT_BYTES=0 \
HTTP_BODY_LIMIT_BYTES=0 \
VALIDATION_TIMEOUT_MS=0 \
pnpm run dev
```

The same variables work with Docker:

```bash
docker run --rm -p 3000:3000 \
  -e VALIDATE_MAX_FILES=0 \
  -e VALIDATE_MAX_FILE_TEXT_BYTES=0 \
  -e VALIDATE_MAX_TOTAL_TEXT_BYTES=0 \
  -e HTTP_BODY_LIMIT_BYTES=0 \
  -e VALIDATION_TIMEOUT_MS=0 \
  ghcr.io/hansbug/sysmlv2-ls-service:0.1.0
```

## Capability reporting

`GET /v1/capabilities` returns the effective limit set. Disabled values are represented as `null` so SDKs can distinguish "unlimited by this service guard" from a numeric cap:

```json
{
  "limits": {
    "validate": {
      "maxFiles": null,
      "maxFileTextBytes": null,
      "maxTotalTextBytes": null,
      "validationTimeoutMs": null
    },
    "http": {
      "bodyLimitBytes": null
    }
  }
}
```

## What each limit protects

| Limit                 | Checked before upstream validation? | Failure response              |
| --------------------- | ----------------------------------- | ----------------------------- |
| `maxFiles`            | Yes, by request schema.             | HTTP `400 bad_request`        |
| `maxFileTextBytes`    | Yes, by request schema.             | HTTP `400 bad_request`        |
| `maxTotalTextBytes`   | Yes, by request schema.             | HTTP `400 bad_request`        |
| `bodyLimitBytes`      | Yes, by Fastify parser.             | HTTP `413 payload_too_large`  |
| `validationTimeoutMs` | Around adapter validation promise.  | HTTP `503 validation_timeout` |

!!! warning "Operational resource controls still matter"
Setting a service-owned limit to `0`, `none`, or `unlimited` disables only that guard. It does not make the Node.js process, the upstream validator, container memory, CPU, reverse proxies, or the operating system unbounded.

## Client-side limit preflight

The Python client defaults to `limits="auto"`, which fetches `/v1/capabilities` and preflights known request sizes before sending large payloads. Use `limits=None`, CLI `--limits none`, or CLI `--no-client-limits` when you intentionally want to skip that client-side preflight.
