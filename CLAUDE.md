# CLAUDE.md

This repository provides a Docker-ready TypeScript microservice wrapping the
legacy Sensmetry `sysml-2ls` SysML v2 language-server core.

`AGENTS.md` is a symlink to this file. Edit this file only.

## Goals

- Expose SysML v2 / KerML validation through a small HTTP API.
- Keep the service runnable locally with Node.js 20+ and publishable as Docker.
- Keep upstream `sysml-2ls` pinned as a git submodule under `upstream/sysml-2ls`.
- Preserve a narrow adapter boundary so state-machine extraction/checking can be
  added without leaking Langium internals into public API contracts.

## Commands

```bash
git submodule update --init --recursive
corepack enable
pnpm install
pnpm run build:upstream
pnpm run ci
pnpm run dev
docker build -t sysmlv2-ls-service:local .
```

## Engineering Rules

- Do not edit upstream submodule files unless the task explicitly asks for an
  upstream fork patch.
- Public API schemas live in `src/contracts.ts`.
- Keep `src/sysml-validator.ts` as the adapter boundary to `sysml-2ls`.
- API responses must use service-owned DTOs, not raw Langium documents.
- Tests should include valid and invalid SysML/KerML examples.
- CI targets Ubuntu and Node.js 20 only; no older Node or cross-platform support
  is required.

## Review Severity

- Critical: service cannot build, run, validate, or Dockerize; unsafe execution;
  API contract returns misleading success; submodule not reproducible.
- Important: missing CI coverage for core path, poor error normalization,
  request isolation issues, unclear setup docs.
- Minor: naming, formatting, optional ergonomics, non-blocking docs polish.
