# sysmlv2-ls-service documentation

`sysmlv2-ls-service` is a Docker-ready TypeScript HTTP wrapper around the pinned Sensmetry `sysml-2ls` SysML v2 / KerML language-server core. It exposes syntax, linking, and semantic validation through service-owned DTOs and a compact HTTP API.

This site is versioned on Read the Docs. It covers this repository's service code, public HTTP contract, Docker behavior, Python client, CLI, generated TypeScript/Python references, and upstream-derived inventories. It deliberately does **not** publish the upstream `sysml-2ls` source tree.

!!! warning "Scope"
The service is a language-validation scaffold, not a formal model checker. State-machine diagnostics surfaced by upstream `sysml-2ls` are structural SysML checks; they do not prove temporal properties such as reachability, liveness, or deadlock freedom.

<div class="doc-card-grid" markdown>

### New service user

Start with the [Quickstart](getting-started/quickstart.md), then use the [HTTP API](service/http-api.md) page for endpoint shapes and error behavior.

### Docker operator

Use the [Docker guide](getting-started/docker.md) for published images, local image builds, smoke checks, and environment-variable limits.

### Python caller

Install `sysmlv2slclient` from [Python install](clients/python/install.md), then choose the [class client API](clients/python/client-api.md) or [CLI](clients/python/cli.md).

### Repository maintainer

Read [Local development](getting-started/local-dev.md), [Architecture](architecture/adapter-boundary.md), and [ADR 0001](adr/0001-docs-system.md) before changing contracts or docs generation.

</div>

## Current public surface

| Surface                | Status      | Primary documentation                                                                            |
| ---------------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| `GET /healthz`         | implemented | [HTTP API](service/http-api.md) and [OpenAPI](reference/openapi.md)                              |
| `GET /v1/capabilities` | implemented | [Capabilities](service/http-api.md#capabilities) and [request limits](service/request-limits.md) |
| `GET /v1/version`      | implemented | [Versioning](service/versioning.md)                                                              |
| `POST /v1/validate`    | implemented | [Validation endpoint](service/http-api.md#validate)                                              |
| Python class client    | implemented | [Python API](clients/python/client-api.md) and [Python reference](reference/python/index.md)     |
| Python CLI `sysmlv2sl` | implemented | [Python CLI](clients/python/cli.md)                                                              |
| Upstream inventory     | generated   | [Upstream inventory](reference/upstream/index.md)                                                |

Planned parse/extraction/model-checking endpoints may appear in the README roadmap, but this documentation only treats implemented behavior as callable API.

## Validation model in one paragraph

Every `POST /v1/validate` request creates one fresh workspace from the submitted files. Imports can resolve between files in that same request, duplicate canonical document URIs are rejected before validation, and no request reuses documents from another request. The response contains service-owned DTOs only; Langium document objects and upstream `sysml-2ls` object shapes are intentionally kept behind the adapter boundary.

## Documentation build model

GitHub Actions owns generated artifacts: OpenAPI summaries, Click CLI help, TypeDoc Markdown, version stamps, and upstream inventories. Read the Docs consumes committed artifacts and runs MkDocs only. To reproduce the full site locally, run:

```bash
git submodule update --init --recursive
corepack enable
pnpm install --frozen-lockfile
pnpm run build:upstream
python -m pip install -r docs/requirements.txt
python -m pip install --no-build-isolation -e clients/python
pnpm run docs:check:full
```
