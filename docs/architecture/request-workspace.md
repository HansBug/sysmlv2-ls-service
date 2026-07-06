# Request workspace

`POST /v1/validate` creates a fresh workspace for each request. This is the central isolation property of the service.

## Document identity

A submitted file can identify itself with one of these fields:

| Field   | Handling                                                                  |
| ------- | ------------------------------------------------------------------------- |
| `uri`   | Parsed as a URI and used as the document URI.                             |
| `path`  | Converted to a file URI with `vscode-uri`.                                |
| neither | Receives an anonymous `memory:///workspace/input-<index>.<language>` URI. |

The `language` field can explicitly select `sysml` or `kerml`; otherwise `.kerml` identifiers infer KerML and other identifiers default to SysML.

## Duplicate checks

The service performs two duplicate checks:

1. Schema-level duplicate explicit `uri`/`path` values are rejected.
2. Route-level duplicate canonical URIs are rejected after URI conversion.

This catches cases such as different path spellings that resolve to the same file URI representation.

## Import resolution

All files in one request are built together. Imports can resolve between those files if upstream `sysml-2ls` linking semantics can resolve the names. No file from a previous request participates in linking.

## Example

```json
{
  "files": [
    {
      "uri": "memory:///library.sysml",
      "text": "package Library { part def Vehicle; }"
    },
    {
      "uri": "memory:///model.sysml",
      "text": "package Model { public import Library::*; part car : Vehicle; }"
    }
  ]
}
```

Both files are visible in the same request workspace. If the second file is sent alone, the import should fail as a linking diagnostic.

## Isolation expectation

Do not add global document caches, shared Langium workspaces, or cross-request mutable state unless the API contract is explicitly redesigned. Cache optimizations must preserve request isolation.
