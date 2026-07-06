# Local development

This repository combines a TypeScript service, a pinned upstream submodule, generated documentation, and an optional Python client. Treat each layer as a separate verification target.

## Toolchain

| Tool           | Required version/policy                     | Purpose                                |
| -------------- | ------------------------------------------- | -------------------------------------- |
| Node.js        | `>=20.19` locally; Docker uses Node.js 24   | Service build, tests, docs generators. |
| pnpm           | `9.15.4` through Corepack                   | Workspace package manager.             |
| Python         | 3.7+ for the client; 3.12 for Read the Docs | Client tests and MkDocs build.         |
| Git submodules | initialized recursively                     | Pinned upstream `sysml-2ls`.           |

Initialize from a clean checkout:

```bash
git submodule update --init --recursive
corepack enable
pnpm install --frozen-lockfile
pnpm run build:upstream
```

## Normal service checks

```bash
pnpm run version:check
pnpm run format:check
pnpm run comments:check
pnpm run typecheck
pnpm run lint
pnpm run test:coverage
pnpm run build
pnpm run smoke:start
pnpm run audit
```

The shorthand gate is:

```bash
pnpm run ci
pnpm run audit
```

## Python client checks

```bash
python -m pip install -e "clients/python[test]"
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
cd clients/python
python -m coverage run --branch -m pytest
python -m coverage report --fail-under=100
```

The Python client is held to 100% branch coverage. Public Python modules, classes, functions, and methods must have English reStructuredText-style docstrings with `:param:`, `:type:`, `:return:`, `:rtype:`, relevant `:raises:`, and `Example::` blocks.

## Documentation checks

Install docs dependencies and the Python client before generating the site:

```bash
python -m pip install -r docs/requirements.txt
python -m pip install --no-build-isolation -e clients/python
pnpm run docs:check:base
pnpm run docs:check:full
```

| Command                           | Scope                                                                  |
| --------------------------------- | ---------------------------------------------------------------------- |
| `pnpm run docs:generate:base`     | Version stamp, CLI help, OpenAPI summary, TypeDoc.                     |
| `pnpm run docs:generate:upstream` | Static inventory from the pinned upstream submodule.                   |
| `pnpm run docs:build`             | `mkdocs build --strict`.                                               |
| `pnpm run docs:check:full`        | OpenAPI lint, all generators, drift checks, secret scan, MkDocs build. |

Preview locally after a successful build:

```bash
python -m http.server 8124 -d site
```

Open <http://127.0.0.1:8124/> and inspect the pages you changed. Do not rely only on `mkdocs build` for visual quality.

## Working tree rules

- Do not edit files under `upstream/sysml-2ls` unless the task explicitly asks for an upstream fork patch.
- `AGENTS.md` is a symlink to `CLAUDE.md`; edit `CLAUDE.md` for automation guidance.
- Generated documentation artifacts are committed intentionally and must be regenerated with the matching script rather than hand-edited when a generator owns them.
- Inspect `git status --short` before committing; a dirty submodule marker for `upstream/sysml-2ls` may be pre-existing and should not be reset without explicit instruction.
