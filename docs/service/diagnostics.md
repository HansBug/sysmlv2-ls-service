# Diagnostics

Diagnostics come from two layers:

1. Langium/Chevrotain document diagnostics: lexing, parsing, and linking.
2. `sysml-2ls` SysML/KerML semantic validators.

`validationChecks: "none"` skips semantic validation only. Lexer and parser failures are still reported and still make `ok: false`. Warnings remain visible in `diagnostics` but do not make `ok` false.

Generated upstream-derived diagnostic inventory is available in [Upstream diagnostics](../reference/upstream/diagnostics-inventory.md).
