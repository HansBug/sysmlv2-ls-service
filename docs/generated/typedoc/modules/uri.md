# Module: uri

## Table of contents

### Functions

- [inferLanguage](uri.md#inferlanguage)
- [makeDocumentUri](uri.md#makedocumenturi)
- [makeDocumentUriKey](uri.md#makedocumenturikey)

## Functions

### inferLanguage

▸ **inferLanguage**(`file`): ``"sysml"`` \| ``"kerml"``

Infer SysML or KerML from explicit language or document identifier.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `file` | `Object` | Submitted file input. |
| `file.language?` | ``"sysml"`` \| ``"kerml"`` | - |
| `file.path?` | `string` | - |
| `file.text` | `string` | - |
| `file.uri?` | `string` | - |

#### Returns

``"sysml"`` \| ``"kerml"``

`kerml` for `.kerml` identifiers, otherwise `sysml`.

**`Example`**

```ts
inferLanguage({ text: "", uri: "memory:///model.kerml" });
```

___

### makeDocumentUri

▸ **makeDocumentUri**(`file`, `index`): `VscodeUri`

Build the request-local Langium document URI for one file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `file` | `Object` | Submitted file input. |
| `file.language?` | ``"sysml"`` \| ``"kerml"`` | - |
| `file.path?` | `string` | - |
| `file.text` | `string` | - |
| `file.uri?` | `string` | - |
| `index` | `number` | Zero-based request file index used for anonymous documents. |

#### Returns

`VscodeUri`

URI used inside the request-local workspace.

**`Example`**

```ts
makeDocumentUri({ text: "package Demo {}" }, 0).toString();
```

___

### makeDocumentUriKey

▸ **makeDocumentUriKey**(`file`, `index`): `string`

Build the canonical duplicate-check key for one file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `file` | `Object` | Submitted file input. |
| `file.language?` | ``"sysml"`` \| ``"kerml"`` | - |
| `file.path?` | `string` | - |
| `file.text` | `string` | - |
| `file.uri?` | `string` | - |
| `index` | `number` | Zero-based request file index. |

#### Returns

`string`

Canonical URI string used for duplicate detection.

**`Example`**

```ts
makeDocumentUriKey({ text: "package Demo {}" }, 0);
```
