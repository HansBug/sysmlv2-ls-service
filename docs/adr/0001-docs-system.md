# ADR 0001: Versioned documentation system

## Status

Accepted for the documentation-system PR.

## Context

The repository needs documentation for several audiences:

- service callers using raw HTTP;
- Docker operators;
- Python SDK and CLI users;
- maintainers changing DTOs, docs generation, or upstream inventory;
- readers who need to understand what the pinned upstream `sysml-2ls` package appears to support.

The site must be versioned, support pull-request previews, and avoid publishing the upstream source tree directly.

## Decision

Use Read the Docs with MkDocs Material as the primary documentation platform. GitHub Pages is not the primary deployment target.

Generated artifacts are committed into `docs/`:

| Artifact           | Generator                                 |
| ------------------ | ----------------------------------------- |
| Version stamp      | `scripts/docs/generate-version-stamp.mjs` |
| CLI help reference | `scripts/docs/generate-cli-docs.mjs`      |
| OpenAPI summary    | `scripts/docs/generate-openapi-docs.mjs`  |
| TypeDoc Markdown   | `scripts/docs/generate-typedoc.mjs`       |
| Upstream inventory | `scripts/docs/inventory-upstream.mjs`     |

Read the Docs installs the Python client and docs requirements, then runs MkDocs against committed generated files. It does not regenerate Node-derived artifacts.

## Rationale

Read the Docs provides versioned builds, pull-request previews, branch builds, tag builds, and stable/latest semantics. MkDocs Material keeps authoring Markdown-first while supporting generated Markdown and Python reference rendering. Committing generated artifacts keeps Read the Docs builds lightweight and avoids requiring Node.js/pnpm generation inside the hosted docs build.

## Consequences

Positive:

- Documentation versions can track release tags and PR previews.
- Generated artifacts are reviewable in PR diffs.
- Upstream inventory can be pinned to the submodule revision used by the service.
- The docs build can run in environments that only install Python docs tooling.

Tradeoffs:

- Contributors must regenerate committed artifacts after changing OpenAPI, CLI behavior, TypeScript public exports, or upstream inventory scripts.
- Browser review is still required for significant docs changes because `mkdocs build --strict` cannot catch every readability issue.
- The upstream inventory is static analysis evidence, not a dynamic guarantee that every discovered row has a service-level reproduction fixture.

## Verification

The full local gate is:

```bash
python -m pip install -r docs/requirements.txt
python -m pip install -e clients/python
pnpm run build:upstream
pnpm run docs:check:full
python -m http.server 8124 -d site
```

After building, inspect the site in a browser at <http://127.0.0.1:8124/> before claiming user-facing documentation is ready.
