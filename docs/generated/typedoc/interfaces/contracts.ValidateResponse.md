# Interface: ValidateResponse

[contracts](../modules/contracts.md).ValidateResponse

Response returned by `POST /v1/validate`.

## Table of contents

### Properties

- [diagnostics](contracts.ValidateResponse.md#diagnostics)
- [files](contracts.ValidateResponse.md#files)
- [meta](contracts.ValidateResponse.md#meta)
- [ok](contracts.ValidateResponse.md#ok)

## Properties

### diagnostics

• **diagnostics**: [`ServiceDiagnostic`](contracts.ServiceDiagnostic.md)[]

___

### files

• **files**: [`FileValidationSummary`](contracts.FileValidationSummary.md)[]

___

### meta

• **meta**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `elapsedMs` | `number` |
| `standardLibrary` | ``"none"`` |
| `validationChecks` | ``"none"`` \| ``"all"`` |

___

### ok

• **ok**: `boolean`
