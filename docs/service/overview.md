# Service overview

The service exposes the pinned upstream `sysml-2ls` language-server core through a narrow HTTP boundary. It accepts SysML v2 / KerML source text, builds a request-local Langium workspace, runs syntax/linking/semantic validation, and returns service-owned DTOs.

## Responsibilities

| Layer              | Owned by this repository                                             | Not owned by this repository                        |
| ------------------ | -------------------------------------------------------------------- | --------------------------------------------------- |
| HTTP routing       | Fastify routes, CORS off by default, error mapping, body limits      | Reverse proxy, authentication, caller identity      |
| Request validation | Zod schemas, duplicate URI/path rejection, service-owned size limits | SysML grammar and semantic rule definitions         |
| Adapter boundary   | Request-local workspace creation, URI generation, DTO conversion     | Langium internals, upstream AST object shapes       |
| Diagnostics        | Severity/code/message/range normalization into DTOs                  | Upstream diagnostic wording and rule implementation |
| Version metadata   | Service version, build args, pinned upstream revision exposure       | Upstream release cadence                            |

## Implemented endpoints

| Endpoint               | Purpose                                                 | Notes                                   |
| ---------------------- | ------------------------------------------------------- | --------------------------------------- |
| `GET /healthz`         | Liveness and service version.                           | Lightweight smoke endpoint.             |
| `GET /v1/capabilities` | Supported languages, modes, and effective limits.       | Disabled limits are returned as `null`. |
| `GET /v1/version`      | Service, upstream, build, and Node.js runtime metadata. | Used by Docker/release smoke checks.    |
| `POST /v1/validate`    | Validate one request-local workspace.                   | Accepts one or more submitted files.    |

Planned parse/state-machine endpoints are intentionally not stubbed. Adding them should include contracts, OpenAPI, tests, docs, and adapter-boundary design in the same change.

## Request-local workspace model

Every validate request is isolated:

1. The service parses the JSON body against service limits.
2. Each submitted file receives a canonical document URI from its `uri`, `path`, or anonymous fallback.
3. Duplicate canonical URIs are rejected before upstream validation.
4. The adapter constructs a fresh Langium workspace from the request files.
5. Imports may resolve across files inside that workspace.
6. The service normalizes diagnostics and discards upstream document objects before responding.

This model lets callers validate multi-file projects without leaking one caller's documents into another caller's request.

## Validation modes

| Option             | Values           | Behavior                                                                                         |
| ------------------ | ---------------- | ------------------------------------------------------------------------------------------------ |
| `standardLibrary`  | `none`           | The current service does not load a SysML standard library.                                      |
| `validationChecks` | `all`, `none`    | `none` skips semantic checks only; lexing and parsing still run.                                 |
| File `language`    | `sysml`, `kerml` | Optional explicit language override. File extension inference defaults to SysML except `.kerml`. |

## Non-goals

- The service is not an ANTLR service; upstream uses Langium/Chevrotain.
- The service is not a temporal model checker.
- The service does not expose raw Langium documents, upstream AST nodes, or upstream service instances.
- The service does not share workspaces between requests.
