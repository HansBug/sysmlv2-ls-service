# Module: app

## Table of contents

### Interfaces

- [AppOptions](../interfaces/app.AppOptions.md)

### Type Aliases

- [ValidateFunction](app.md#validatefunction)

### Functions

- [buildApp](app.md#buildapp)

## Type Aliases

### ValidateFunction

Ƭ **ValidateFunction**: (`request`: [`ValidateRequest`](contracts.md#validaterequest)) => `Promise`\<[`ValidateResponse`](../interfaces/contracts.ValidateResponse.md)\>

Validator callback used by the Fastify route and by tests or embedders.

#### Type declaration

▸ (`request`): `Promise`\<[`ValidateResponse`](../interfaces/contracts.ValidateResponse.md)\>

##### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `request` | [`ValidateRequest`](contracts.md#validaterequest) | Parsed validate request DTO. |

##### Returns

`Promise`\<[`ValidateResponse`](../interfaces/contracts.ValidateResponse.md)\>

## Functions

### buildApp

▸ **buildApp**(`options?`): `Promise`\<`FastifyInstance`\>

Build a configured Fastify application.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `options` | [`AppOptions`](../interfaces/app.AppOptions.md) | Optional app construction settings. |

#### Returns

`Promise`\<`FastifyInstance`\>

Ready-to-start Fastify application instance.

**`Example`**

```ts
const app = await buildApp({ logger: false });
const response = await app.inject({ method: "GET", url: "/healthz" });
```
