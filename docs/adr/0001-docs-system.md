# ADR 0001: Versioned documentation system

## Decision

Use Read the Docs with MkDocs Material as the primary documentation platform. GitHub Pages is not the primary deployment target.

## Rationale

Read the Docs provides versioned builds, pull request previews, tag builds, and stable/latest version semantics. MkDocs Material keeps the source format Markdown-first while allowing generated Markdown from OpenAPI, TypeDoc, CLI help, and upstream inventory scripts.

## Consequences

GitHub Actions owns generated documentation artifacts. Read the Docs consumes committed artifacts and runs MkDocs only; it must not regenerate Node-derived artifacts.
