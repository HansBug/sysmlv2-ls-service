# Module: limits

## Table of contents

### Interfaces

- [HttpLimits](../interfaces/limits.HttpLimits.md)
- [ServiceLimits](../interfaces/limits.ServiceLimits.md)
- [ValidateLimits](../interfaces/limits.ValidateLimits.md)

### Variables

- [DEFAULT\_HTTP\_BODY\_LIMIT\_BYTES](limits.md#default_http_body_limit_bytes)
- [DEFAULT\_MAX\_FILES](limits.md#default_max_files)
- [DEFAULT\_MAX\_FILE\_TEXT\_BYTES](limits.md#default_max_file_text_bytes)
- [DEFAULT\_MAX\_TOTAL\_TEXT\_BYTES](limits.md#default_max_total_text_bytes)
- [DEFAULT\_SERVICE\_LIMITS](limits.md#default_service_limits)
- [DEFAULT\_VALIDATION\_TIMEOUT\_MS](limits.md#default_validation_timeout_ms)

### Functions

- [fastifyBodyLimit](limits.md#fastifybodylimit)
- [resolveServiceLimits](limits.md#resolveservicelimits)

## Variables

### DEFAULT\_HTTP\_BODY\_LIMIT\_BYTES

• `Const` **DEFAULT\_HTTP\_BODY\_LIMIT\_BYTES**: `number`

Default Fastify HTTP body limit in bytes.

___

### DEFAULT\_MAX\_FILES

• `Const` **DEFAULT\_MAX\_FILES**: ``64``

Default maximum number of files in one validate request.

___

### DEFAULT\_MAX\_FILE\_TEXT\_BYTES

• `Const` **DEFAULT\_MAX\_FILE\_TEXT\_BYTES**: `number`

Default maximum UTF-8 byte size for one file's text.

___

### DEFAULT\_MAX\_TOTAL\_TEXT\_BYTES

• `Const` **DEFAULT\_MAX\_TOTAL\_TEXT\_BYTES**: `number`

Default maximum total UTF-8 byte size for all submitted files.

___

### DEFAULT\_SERVICE\_LIMITS

• `Const` **DEFAULT\_SERVICE\_LIMITS**: [`ServiceLimits`](../interfaces/limits.ServiceLimits.md)

Default service-owned limits documented in the README.

___

### DEFAULT\_VALIDATION\_TIMEOUT\_MS

• `Const` **DEFAULT\_VALIDATION\_TIMEOUT\_MS**: ``30000``

Default validation timeout in milliseconds.

## Functions

### fastifyBodyLimit

▸ **fastifyBodyLimit**(`limits`): `number`

Convert HTTP limits into a Fastify-compatible body limit.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `limits` | [`ServiceLimits`](../interfaces/limits.ServiceLimits.md) | Effective service limits. |

#### Returns

`number`

Fastify body limit in bytes.

**`Example`**

```ts
fastifyBodyLimit(DEFAULT_SERVICE_LIMITS);
```

___

### resolveServiceLimits

▸ **resolveServiceLimits**(`env?`): [`ServiceLimits`](../interfaces/limits.ServiceLimits.md)

Resolve effective service limits from environment variables.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `env` | `ProcessEnv` | `process.env` | Environment-like object. Defaults to `process.env`. |

#### Returns

[`ServiceLimits`](../interfaces/limits.ServiceLimits.md)

Effective service limits.

**`Throws`**

Error when a configured limit is not a positive integer, `0`,
`"none"`, or `"unlimited"`.

**`Example`**

```ts
resolveServiceLimits({ HTTP_BODY_LIMIT_BYTES: "0" }).http.bodyLimitBytes;
```
