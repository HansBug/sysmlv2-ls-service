# Upstream import resolution

!!! info "Inventory context"

    This page is checked against upstream `sysml-2ls` package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`.

The service submits all files in a validation request as one request-local workspace. Imports can resolve among those submitted files when upstream linking semantics can resolve the referenced names.

## Service-owned behavior

| Concern               | Behavior                                                |
| --------------------- | ------------------------------------------------------- |
| Workspace lifetime    | One fresh workspace per `POST /v1/validate` request.    |
| Cross-file imports    | Possible among files in the same request.               |
| Cross-request imports | Not possible; requests are isolated.                    |
| URI construction      | Owned by `src/uri.ts`.                                  |
| Duplicate rejection   | Owned by request schema and route canonical URI checks. |
| Link semantics        | Owned by upstream `sysml-2ls`.                          |

## Example

```json
{
  "files": [
    {
      "uri": "memory:///Library.sysml",
      "text": "package Library { part def Vehicle; }"
    },
    {
      "uri": "memory:///Model.sysml",
      "text": "package Model { public import Library::*; part car : Vehicle; }"
    }
  ]
}
```

Both documents are built together, so `Model` can see `Library` if the import is valid for upstream. If `Library.sysml` is omitted, the service should return a `linking-error` diagnostic rather than a service HTTP error.

## Client implications

- `validate_files()` and `validate_directory()` should submit related files together.
- Prefer stable `memory:///` URIs when validating from remote clients or CI.
- Use `file` URI/path mode only when absolute local paths are meaningful for the service environment.
- Keep generated directory URIs unique after normalization.
