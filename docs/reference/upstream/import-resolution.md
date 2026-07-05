# Upstream import resolution

!!! info "Inventory context"
This page is checked against upstream `sysml-2ls` package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`.

The service submits all files in a validation request as one request-local workspace. Imports can resolve among those submitted files. No request shares documents with another request.

The upstream language server still owns SysML/KerML linking semantics; this service owns URI canonicalization and duplicate canonical URI rejection.
