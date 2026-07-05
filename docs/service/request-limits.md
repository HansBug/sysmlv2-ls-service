# Request limits

The default service-owned limits are documented in the README and reflected by `GET /v1/capabilities`:

| Limit                      | Default   | Disable with                      |
| -------------------------- | --------- | --------------------------------- |
| Validate files per request | `64`      | `VALIDATE_MAX_FILES=0`            |
| UTF-8 bytes per file       | `512 KiB` | `VALIDATE_MAX_FILE_TEXT_BYTES=0`  |
| Total submitted text       | `1 MiB`   | `VALIDATE_MAX_TOTAL_TEXT_BYTES=0` |
| HTTP body limit            | `5 MiB`   | `HTTP_BODY_LIMIT_BYTES=0`         |
| Validation timeout         | `30 s`    | `VALIDATION_TIMEOUT_MS=0`         |

Values `0`, `none`, and `unlimited` disable only the corresponding service-owned guard. They do not make the process or upstream language server resource-unbounded.
