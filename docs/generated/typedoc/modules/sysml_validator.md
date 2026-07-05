# Module: sysml-validator

## Table of contents

### Functions

- [validateSysML](sysml_validator.md#validatesysml)

## Functions

### validateSysML

▸ **validateSysML**(`request`): `Promise`\<[`ValidateResponse`](../interfaces/contracts.ValidateResponse.md)\>

Validate a request-local SysML/KerML workspace.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `request` | `Object` | `undefined` | Parsed validate request. |
| `request.files` | \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] | `filesSchema` | - |
| `request.standardLibrary` | ``"none"`` | `undefined` | - |
| `request.validationChecks` | ``"none"`` \| ``"all"`` | `undefined` | - |

#### Returns

`Promise`\<[`ValidateResponse`](../interfaces/contracts.ValidateResponse.md)\>

Service-owned validation response.

**`Example`**

```ts
await validateSysML({
  files: [{ text: "package Demo {}", uri: "memory:///demo.sysml" }],
  standardLibrary: "none",
  validationChecks: "all"
});
```
