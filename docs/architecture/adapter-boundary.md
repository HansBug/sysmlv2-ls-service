# Adapter boundary

`src/sysml-validator.ts` is the boundary between the HTTP service and upstream `sysml-2ls`. Public DTOs remain in `src/contracts.ts`; downstream callers should never depend on Langium or upstream object shapes.
