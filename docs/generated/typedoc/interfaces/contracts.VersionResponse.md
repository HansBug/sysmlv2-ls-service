# Interface: VersionResponse

[contracts](../modules/contracts.md).VersionResponse

Response returned by `GET /v1/version`.

## Table of contents

### Properties

- [build](contracts.VersionResponse.md#build)
- [service](contracts.VersionResponse.md#service)
- [upstream](contracts.VersionResponse.md#upstream)

## Properties

### build

• **build**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `date` | `string` |
| `nodeVersion` | `string` |

___

### service

• **service**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `name` | `string` |
| `revision` | `string` |
| `sourceRepository` | `string` |
| `version` | `string` |

___

### upstream

• **upstream**: `Object`

#### Type declaration

| Name | Type |
| :------ | :------ |
| `sysml2ls` | \{ `packageName`: `string` ; `repository`: `string` ; `revision`: `string` ; `version`: `string`  } |
| `sysml2ls.packageName` | `string` |
| `sysml2ls.repository` | `string` |
| `sysml2ls.revision` | `string` |
| `sysml2ls.version` | `string` |
