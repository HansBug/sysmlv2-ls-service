# Adapter boundary

`src/sysml-validator.ts` is the boundary between public service DTOs and upstream `sysml-2ls` / Langium internals.

## Why this boundary exists

The repository needs a stable HTTP API that can be used from Node.js, Python, Docker, and microservice callers without requiring those callers to understand Langium documents, upstream service registries, or AST classes. Keeping the adapter narrow also leaves room for future state-machine extraction or model-checking layers above validation.

## Inputs and outputs

| Direction      | Type                                          | Ownership                         |
| -------------- | --------------------------------------------- | --------------------------------- |
| Into adapter   | `ValidateRequest` from `src/contracts.ts`     | Service-owned DTO.                |
| Internal       | Langium documents built by upstream factories | Upstream implementation detail.   |
| Internal       | `createSysMLServices` configuration           | Adapter-owned integration detail. |
| Out of adapter | `ValidateResponse` from `src/contracts.ts`    | Service-owned DTO.                |

No route returns raw Langium documents or upstream object shapes.

## Validation sequence

1. Route code parses and limit-checks the JSON request.
2. Route code rejects duplicate canonical document URIs.
3. Adapter creates upstream SysML services with workspace initialization disabled.
4. Adapter creates one Langium document per submitted file.
5. Adapter invokes the upstream document builder with request options.
6. Adapter normalizes document diagnostics and builds per-file summaries.
7. Adapter returns a DTO with `ok`, `diagnostics`, `files`, and `meta`.

## Configuration policy

The current adapter uses `standardLibrary: false` and accepts only `standardLibrary: "none"` from callers. A future standard-library feature should add reproducible library path/cache ownership before expanding the public enum.

## Extension guidance

Add new capabilities above the adapter boundary rather than leaking internals through HTTP responses. For example, a future state-machine extraction endpoint should define service-owned extraction DTOs, tests, and OpenAPI schemas, then use adapter-owned internal helpers to inspect upstream documents.
