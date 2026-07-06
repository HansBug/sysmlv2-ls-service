# Upstream limitations

!!! info "Inventory context"

    This page is checked against upstream `sysml-2ls` package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`.

The upstream core provides syntax, linking, and semantic validation through Langium/Chevrotain. It is not a temporal model checker, and this service does not add formal verification on top of it.

## What the inventory can say

| Inventory           | Evidence                                                             | Safe interpretation                                               |
| ------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Semantic checks     | Validator method names and decorators in upstream TypeScript source. | A structural check appears to exist in the pinned submodule.      |
| Diagnostic messages | Static message literals near discovered validator methods.           | The upstream code contains this wording or template near a check. |
| Grammar surface     | Top-level Langium grammar rules/type aliases.                        | The pinned grammar source declares these rules or aliases.        |

## What the inventory cannot say yet

- It does not prove every row is reachable from a minimal service request.
- It does not guarantee exact diagnostic wording after upstream templating.
- It does not guarantee runtime severity for every semantic check.
- It does not replace upstream release notes or language specification text.
- It does not prove state-machine temporal properties.

## State-machine caution

Rows such as `validateState*`, `validateTransition*`, `validateTriggerInvocation*`, and `validateExhibitStateUsageReference` are structural SysML validation checks. They may catch malformed state/transition modeling constructs, but they do not prove reachability, deadlock freedom, liveness, CTL/LTL properties, or scenario completeness.

## Future improvement path

A later inventory version could add dynamic fixtures for selected diagnostics, compare compiled artifacts against TypeScript source, and classify checks into higher-level SysML feature families. Those additions should remain generated and reproducible rather than manually curated only.
