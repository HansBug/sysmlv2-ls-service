# Interface: CapabilitiesResponse

[contracts](../modules/contracts.md).CapabilitiesResponse

Response returned by `GET /v1/capabilities`.

## Table of contents

### Properties

- [languages](contracts.CapabilitiesResponse.md#languages)
- [limits](contracts.CapabilitiesResponse.md#limits)
- [standardLibrary](contracts.CapabilitiesResponse.md#standardlibrary)
- [validationChecks](contracts.CapabilitiesResponse.md#validationchecks)

## Properties

### languages

• **languages**: \{ `extensions`: `string`[] ; `id`: ``"sysml"`` \| ``"kerml"``  }[]

___

### limits

• **limits**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `http` | [`HttpLimits`](limits.HttpLimits.md) |
| `validate` | [`ValidateLimits`](limits.ValidateLimits.md) |

___

### standardLibrary

• **standardLibrary**: ``"none"``[]

___

### validationChecks

• **validationChecks**: (``"none"`` \| ``"all"``)[]
