# Module: contracts

## Table of contents

### Interfaces

- [CapabilitiesResponse](../interfaces/contracts.CapabilitiesResponse.md)
- [FileValidationSummary](../interfaces/contracts.FileValidationSummary.md)
- [HealthResponse](../interfaces/contracts.HealthResponse.md)
- [ServiceDiagnostic](../interfaces/contracts.ServiceDiagnostic.md)
- [SourcePosition](../interfaces/contracts.SourcePosition.md)
- [SourceRange](../interfaces/contracts.SourceRange.md)
- [ValidateResponse](../interfaces/contracts.ValidateResponse.md)
- [VersionResponse](../interfaces/contracts.VersionResponse.md)

### Type Aliases

- [DiagnosticSeverityName](contracts.md#diagnosticseverityname)
- [SysMLFileInput](contracts.md#sysmlfileinput)
- [ValidateRequest](contracts.md#validaterequest)

### Variables

- [sysmlFileSchema](contracts.md#sysmlfileschema)
- [validateRequestSchema](contracts.md#validaterequestschema)

### Functions

- [makeValidateRequestSchema](contracts.md#makevalidaterequestschema)

## Type Aliases

### DiagnosticSeverityName

Ƭ **DiagnosticSeverityName**: ``"error"`` \| ``"warning"`` \| ``"information"`` \| ``"hint"``

Stable diagnostic severity names exposed by the service.

___

### SysMLFileInput

Ƭ **SysMLFileInput**: `z.infer`\<typeof [`sysmlFileSchema`](contracts.md#sysmlfileschema)\>

Inferred TypeScript shape for one submitted file.

___

### ValidateRequest

Ƭ **ValidateRequest**: `z.infer`\<typeof [`validateRequestSchema`](contracts.md#validaterequestschema)\>

Inferred TypeScript shape for a validate request.

## Variables

### sysmlFileSchema

• `Const` **sysmlFileSchema**: `ZodObject`\<\{ `language`: `ZodOptional`\<`ZodEnum`\<[``"sysml"``, ``"kerml"``]\>\> ; `path`: `ZodOptional`\<`ZodString`\> ; `text`: `ZodString` ; `uri`: `ZodOptional`\<`ZodString`\>  }, ``"strip"``, `ZodTypeAny`, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }\>

One submitted SysML/KerML document.

The caller may identify the document with either a URI or a path. Anonymous
documents receive request-local memory URIs later in the adapter boundary.

___

### validateRequestSchema

• `Const` **validateRequestSchema**: `ZodEffects`\<`ZodObject`\<\{ `files`: `ZodArray`\<`ZodObject`\<\{ `language`: `ZodOptional`\<`ZodEnum`\<[``"sysml"``, ``"kerml"``]\>\> ; `path`: `ZodOptional`\<`ZodString`\> ; `text`: `ZodString` ; `uri`: `ZodOptional`\<`ZodString`\>  }, ``"strip"``, `ZodTypeAny`, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }\>, ``"many"``\> = filesSchema; `standardLibrary`: `ZodDefault`\<`ZodEnum`\<[``"none"``]\>\> ; `validationChecks`: `ZodDefault`\<`ZodEnum`\<[``"all"``, ``"none"``]\>\>  }, ``"strip"``, `ZodTypeAny`, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>

Default validate request schema using default service limits.

## Functions

### makeValidateRequestSchema

▸ **makeValidateRequestSchema**(`limits`): `ZodEffects`\<`ZodObject`\<\{ `files`: `ZodArray`\<`ZodObject`\<\{ `language`: `ZodOptional`\<`ZodEnum`\<[``"sysml"``, ``"kerml"``]\>\> ; `path`: `ZodOptional`\<`ZodString`\> ; `text`: `ZodString` ; `uri`: `ZodOptional`\<`ZodString`\>  }, ``"strip"``, `ZodTypeAny`, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }\>, ``"many"``\> = filesSchema; `standardLibrary`: `ZodDefault`\<`ZodEnum`\<[``"none"``]\>\> ; `validationChecks`: `ZodDefault`\<`ZodEnum`\<[``"all"``, ``"none"``]\>\>  }, ``"strip"``, `ZodTypeAny`, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>

Build the validate request schema for a concrete set of service limits.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `limits` | [`ServiceLimits`](../interfaces/limits.ServiceLimits.md) | Effective service-owned limits. A `null` limit disables only that service-owned guard. |

#### Returns

`ZodEffects`\<`ZodObject`\<\{ `files`: `ZodArray`\<`ZodObject`\<\{ `language`: `ZodOptional`\<`ZodEnum`\<[``"sysml"``, ``"kerml"``]\>\> ; `path`: `ZodOptional`\<`ZodString`\> ; `text`: `ZodString` ; `uri`: `ZodOptional`\<`ZodString`\>  }, ``"strip"``, `ZodTypeAny`, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }, \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }\>, ``"many"``\> = filesSchema; `standardLibrary`: `ZodDefault`\<`ZodEnum`\<[``"none"``]\>\> ; `validationChecks`: `ZodDefault`\<`ZodEnum`\<[``"all"``, ``"none"``]\>\>  }, ``"strip"``, `ZodTypeAny`, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary`: ``"none"`` ; `validationChecks`: ``"none"`` \| ``"all"``  }, \{ `files`: \{ `language?`: ``"sysml"`` \| ``"kerml"`` ; `path?`: `string` ; `text`: `string` ; `uri?`: `string`  }[] = filesSchema; `standardLibrary?`: ``"none"`` ; `validationChecks?`: ``"none"`` \| ``"all"``  }\>

Zod schema for `POST /v1/validate` request bodies.

**`Example`**

```ts
const schema = makeValidateRequestSchema(DEFAULT_SERVICE_LIMITS);
const request = schema.parse({ files: [{ text: "package Demo {}" }] });
```
