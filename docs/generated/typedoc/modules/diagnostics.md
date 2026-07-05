# Module: diagnostics

## Table of contents

### Functions

- [normalizeDiagnostic](diagnostics.md#normalizediagnostic)

## Functions

### normalizeDiagnostic

▸ **normalizeDiagnostic**(`diagnostic`, `uri`, `defaultSource?`): [`ServiceDiagnostic`](../interfaces/contracts.ServiceDiagnostic.md)

Normalize one upstream diagnostic into the public service DTO.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `diagnostic` | `Diagnostic` | `undefined` | Langium or language-server diagnostic. |
| `uri` | `string` | `undefined` | Public document URI associated with the diagnostic. |
| `defaultSource` | `string` | `"sysml-2ls"` | Source value used when the upstream diagnostic omits one. |

#### Returns

[`ServiceDiagnostic`](../interfaces/contracts.ServiceDiagnostic.md)

Service-owned diagnostic DTO.

**`Example`**

```ts
normalizeDiagnostic(diagnostic, "memory:///demo.sysml", "sysml-2ls");
```
