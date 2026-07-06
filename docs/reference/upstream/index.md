# Upstream-derived inventory

This section summarizes static data derived from the pinned `upstream/sysml-2ls` submodule. It does not publish upstream source files, and it should not be read as a promise that every upstream diagnostic has a stable service-level reproduction fixture.

## Pages

| Page                                              | What it answers                                                                                |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [Diagnostics inventory](diagnostics-inventory.md) | Which diagnostic message patterns are statically associated with discovered validation checks? |
| [Semantic checks](semantic-checks.md)             | Which validator methods and AST decorators were discovered?                                    |
| [Grammar surface](grammar-surface.md)             | Which top-level Langium grammar rules and type aliases were found?                             |
| [Import resolution](import-resolution.md)         | How does service request-local workspace behavior interact with upstream linking?              |
| [Limitations](limitations.md)                     | What should readers not infer from the static inventory?                                       |

## Evidence policy

The generator scans upstream TypeScript grammar and validator source, while also checking that compiled JS/d.ts artifacts exist after `pnpm run build:upstream`. Compiled artifacts are presence evidence only in this first inventory version; they are not the primary parser evidence.

## Regeneration

```bash
pnpm run build:upstream
pnpm run docs:generate:upstream
pnpm run docs:generated:check:full
```

The committed inventory records the upstream package version and submodule revision. The MkDocs version hook appends the service repository revision/source date when the site is built.

## Interpretation guardrails

- Static rows indicate discovered source patterns, not dynamic proof of reachability.
- Message patterns may include template placeholders from upstream code.
- Low-confidence diagnostics mean the script found a check but no direct message literal.
- State-machine-related checks are structural SysML checks, not temporal verification.
