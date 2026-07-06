# Diagnostics

Diagnostics returned from `POST /v1/validate` are service-owned DTOs normalized from Langium and upstream `sysml-2ls` diagnostics. HTTP request failures are not diagnostics.

## Diagnostic layers

| Layer               | Typical codes                                                                                          | Owned by                        | Notes                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------- | ------------------------------------------------------------- |
| Lexing              | `lexing-error`                                                                                         | Langium/Chevrotain              | Input cannot be tokenized.                                    |
| Parsing             | `parsing-error`                                                                                        | Langium/Chevrotain              | Token stream does not match SysML/KerML grammar.              |
| Linking             | `linking-error`                                                                                        | Langium/upstream workspace      | References cannot resolve inside the request-local workspace. |
| Semantic validation | `validateFeatureTyping`, `validatePartUsageTyping`, `validateTransitionUsageSuccession`, and many more | Upstream `sysml-2ls` validators | Structural SysML/KerML model checks.                          |

`validationChecks: "none"` skips semantic validation only. Lexer and parser failures still run and still make `ok: false`.

## Response shape

```json
{
  "severity": "error",
  "source": "sysml-2ls",
  "code": "parsing-error",
  "message": "Expecting: one of these possible Token sequences: ...",
  "uri": "memory:///broken.sysml",
  "range": {
    "start": { "line": 0, "character": 33 },
    "end": { "line": 0, "character": 33 }
  }
}
```

Severity names are normalized to `error`, `warning`, `information`, or `hint`. Unknown diagnostic codes are preserved rather than dropped.

## `ok` calculation

The service returns `ok: false` when either condition is true:

- any file has lexer or parser errors; or
- any normalized diagnostic has severity `error`.

Warnings remain visible in `diagnostics` but do not make `ok` false by themselves.

## Common examples

| Trigger                                                    | Expected category                                 | Typical remediation                                                           |
| ---------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| `package BrokenSyntax { part def }`                        | `parsing-error`                                   | Complete or remove the malformed declaration.                                 |
| `public import Missing::*;`                                | `linking-error`                                   | Submit the defining file in the same request or correct the qualified name.   |
| Two `part def Vehicle;` declarations in the same namespace | `validateNamespaceDistinguishability` warning     | Rename, qualify, or merge duplicate members.                                  |
| `part loose;`                                              | `validateFeatureTyping` / part typing diagnostics | Type the feature with a valid definition.                                     |
| Invalid state/transition ownership                         | `validateState*` or `validateTransition*`         | Fix structural SysML ownership and typing; this is not temporal verification. |

## Inventory links

- [Upstream diagnostics inventory](../reference/upstream/diagnostics-inventory.md) lists statically discovered upstream diagnostic message patterns.
- [Upstream semantic checks](../reference/upstream/semantic-checks.md) lists validator methods and decorators.
- [Upstream grammar surface](../reference/upstream/grammar-surface.md) lists top-level Langium grammar rules and type aliases.
