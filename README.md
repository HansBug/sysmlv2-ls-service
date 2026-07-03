# sysmlv2-ls-service

Docker-ready SysML v2 validation microservice built on top of Sensmetry's legacy
[`sysml-2ls`](https://github.com/sensmetry/sysml-2ls) language-server core.

The service exposes a small HTTP API for parsing and validating SysML v2 / KerML
text from Node.js or Docker workflows. It is intended as a research and
integration scaffold: `sysml-2ls` provides the textual language frontend, while
project-specific state-machine extraction and checking can be added above this
API.

## Scope

Current API:

- `GET /healthz`
- `GET /v1/capabilities`
- `POST /v1/validate`

Planned API:

- `POST /v1/parse`
- `POST /v1/extract/state-machines`
- `POST /v1/check/state-machines`

This service performs syntax/linking/semantic validation available through
`sysml-2ls`. It is not, by itself, a formal model checker.

Files in one validation request are built as a single request-local workspace, so
imports between submitted files can resolve. Requests are isolated from each
other.

## Repository Layout

```text
.
├── src/                     # TypeScript API service and sysml-2ls adapter
├── tests/                   # Vitest unit/integration tests
├── examples/                # Small request/model examples
├── upstream/sysml-2ls       # Git submodule pinned to upstream sysml-2ls
├── Dockerfile
└── .github/workflows/ci.yml
```

## Prerequisites

- Node.js 20 or newer
- pnpm
- Git submodules initialized

```bash
git submodule update --init --recursive
corepack enable
pnpm install
pnpm run build:upstream
```

## Local Development

Run tests and checks:

```bash
pnpm run ci
```

Start the service:

```bash
cp .env.example .env
pnpm run dev
```

Validate a simple model:

```bash
curl -sS -X POST http://localhost:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///demo.sysml","text":"package Demo { part def Vehicle; }"}]}' \
  | jq
```

## Docker

Build:

```bash
docker build -t sysmlv2-ls-service:local .
```

Run:

```bash
docker run --rm -p 3000:3000 sysmlv2-ls-service:local
```

Smoke test:

```bash
curl -fsS http://localhost:3000/healthz
```

## Validation Request

```json
{
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "text": "package Demo { part def Vehicle; }"
    }
  ],
  "standardLibrary": "none",
  "validationChecks": "all"
}
```

Limits:

- Maximum files per request: 64
- Maximum text per file: 512 KiB
- Maximum total text per request: 1 MiB
- Duplicate `uri`/`path` values are rejected

`validationChecks: "none"` skips semantic checks only. Lexer and parser failures
still return `ok: false`.

Response:

```json
{
  "ok": true,
  "diagnostics": [],
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "language": "sysml",
      "parserErrors": 0,
      "lexerErrors": 0,
      "diagnostics": 0
    }
  ],
  "meta": {
    "standardLibrary": "none",
    "validationChecks": "all",
    "elapsedMs": 12.34
  }
}
```

## Notes on `sysml-2ls`

`sysml-2ls` is a legacy/deprecated open-source SysML v2 language server. It uses
Langium/Chevrotain rather than ANTLR. The submodule is intentionally pinned so
CI and Docker builds are reproducible.

The current API runs validation without a SysML standard library
(`standardLibrary: "none"`). Standard-library-backed validation should be added
as an explicit configuration feature once the service owns a reproducible local
library path or cache.

## License

This repository is a service scaffold. The vendored upstream submodule retains
its original license terms. Review upstream licensing before redistribution.
