# CLAUDE.md

This repository provides a Docker-ready TypeScript microservice wrapping the
legacy Sensmetry `sysml-2ls` SysML v2 language-server core.

`AGENTS.md` is a symlink to this file. Edit `CLAUDE.md` only; do not create a
second project guidance file unless the user explicitly asks for it.

## Mission

- Expose SysML v2 / KerML syntax, linking, and semantic validation through a
  small HTTP API suitable for Node.js, Python, Docker, and microservice callers.
- Keep the service runnable locally with Node.js 20.19+ and publishable as a
  Docker image using the Node.js 24 runtime.
- Keep upstream `sysml-2ls` pinned as a git submodule under
  `upstream/sysml-2ls`.
- Preserve a narrow adapter boundary so later state-machine extraction or model
  checking can be added above this service without leaking Langium internals into
  public API contracts.

This repository is a service scaffold. It is not currently a formal model
checker. State-machine related diagnostics exposed by upstream `sysml-2ls` are
structural SysML validation checks, not temporal verification results.

## Technology Stack

- Runtime/API: TypeScript ESM, Fastify, Zod, Langium, `@fastify/cors`.
- Validation core: upstream `sysml-2ls` packages
  `syside-base`, `syside-protocol`, and `syside-languageserver`.
- Grammar/tooling: Langium/Chevrotain via upstream `sysml-2ls`; this repository
  does not use ANTLR.
- Package manager: pnpm 9.15.4 through Corepack.
- Local supported Node.js: `>=20.19`.
- CI matrix: Ubuntu, Node.js 20.19 and 24.
- Docker runtime: `node:24-bookworm-slim`.

## Repository Map

- `src/contracts.ts` owns public request/response DTOs, Zod request schemas, and
  schema-level request validation such as explicit duplicate URI/path checks.
- `src/app.ts` owns Fastify routes, HTTP errors, timeout behavior, body limits,
  canonical duplicate URI rejection, and conversion of schema failures into HTTP
  responses.
- `src/sysml-validator.ts` is the adapter boundary to upstream `sysml-2ls`.
- `src/diagnostics.ts` normalizes Langium/upstream diagnostics into service DTOs.
- `src/uri.ts` owns request-local document URI canonicalization.
- `src/version.ts` owns `/v1/version` metadata composition.
- `VERSION` is the service version source of truth; `package.json.version` must
  mirror it.
- `scripts/check-version.mjs` enforces `VERSION` and `package.json.version`
  consistency.
- `examples/python/` contains the stdlib Python API example and should remain a
  working smoke example.
- `upstream/sysml-2ls` is a pinned submodule. Treat it as vendored upstream.

## Essential Commands

```bash
git submodule update --init --recursive
corepack enable
pnpm install --frozen-lockfile
pnpm run build:upstream
pnpm run version:check
pnpm run format:check
pnpm run docs:check
pnpm run ci
pnpm run audit
pnpm run dev
docker build -t sysmlv2-ls-service:local .

python -m pip install -e "clients/python[test]"
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
```

Use `pnpm install --frozen-lockfile` in CI-like validation. Use plain
`pnpm install` only when intentionally updating dependency metadata.

## Code Style and Documentation Discipline

These rules apply to service-owned code only. Exclude `upstream/sysml-2ls`,
generated build output, dependency directories, and coverage artifacts.

Python client rules:

- Runtime code lives under `clients/python/src/sysmlv2slclient`.
- Public modules, classes, functions, and methods must use English
  reStructuredText docstrings following PEP 257 / Sphinx style.
- Module docstrings must explain the module's responsibility and its place in
  the SDK. Public class/function/method docstrings must document `:param:`,
  `:type:`, `:return:`, `:rtype:`, relevant `:raises:`, and include an
  `Example::` block.
- `clients/python/src/sysmlv2slclient/__init__.py` must keep a table-shaped
  module roadmap that explains the main exports and their purposes.
- Inline code in Python docstrings uses double-backtick reST literals, never
  Markdown single backticks or Google/NumPy style sections.
- Python formatting and linting use Ruff:

```bash
python -m ruff format clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
```

JavaScript/TypeScript rules:

- Service-owned JS/TS code lives under `src/`, `tests/`, and `scripts/`.
  `upstream/` is never part of service code style or documentation checks.
- ESLint is the code-quality and bug-risk checker. Prettier is the formatter.
  Do not move formatter-only concerns into ESLint rules.
- Public/exported TypeScript APIs require TSDoc/JSDoc comments that explain
  responsibility, parameters, return values, and error semantics where relevant.
- Core modules need a module-level JSDoc block explaining ownership and
  boundaries, especially contracts, routes, limits, diagnostics, URI handling,
  validator adapter, and version metadata.
- `pnpm run docs:check` scans `src/`, `tests/`, and `scripts/`; it requires
  module-level JSDoc for `src/` modules, requires JSDoc before exported
  declarations in all three roots, and rejects empty `/** */` placeholder
  comments.
- JS/TS formatting, linting, and documentation checks use:

```bash
pnpm run format
pnpm run format:check
pnpm run lint
pnpm run docs:check
```

Before claiming a code change ready, run the appropriate language checks plus
the normal test and audit gates. Do not weaken doc/comment check scripts to
avoid writing documentation; update the docs or the explicit allowlist only when
the public surface genuinely changes.

## API Contract

Current API:

- `GET /healthz`
- `GET /v1/capabilities`
- `GET /v1/version`
- `POST /v1/validate`

Planned API surface is documented in `README.md`; do not add planned endpoints
as stubs unless the user asks for implementation.

Rules:

- API responses must use service-owned DTOs from `src/contracts.ts`, never raw
  Langium documents or upstream object shapes.
- `POST /v1/validate` builds one request-local workspace. Imports can resolve
  across files in the same request, and requests must remain isolated from each
  other.
- `validationChecks: "none"` skips semantic validation only. Lexer and parser
  failures still make `ok: false`.
- Warnings remain visible in `diagnostics` but do not make `ok` false. Any
  normalized diagnostic with severity `error` makes `ok` false.
- HTTP schema, payload, timeout, and internal service errors are service errors,
  not SysML diagnostics.
- Do not expose internal exception messages in 5xx responses.
- Preserve request limits from `README.md` unless the task explicitly changes
  them: 64 files, 512 KiB per file, 1 MiB total text, 5 MiB HTTP body limit,
  default validation timeout 30 seconds.

## Version Metadata Rules

`VERSION` is canonical for the service version.

Required invariants:

- `VERSION` and `package.json.version` must match exactly.
- `pnpm run version:check` must pass before commits, Docker builds, and releases.
- Tests must not hard-code the current service version. Read `VERSION` or call
  `getVersionInfo()` instead.
- Tests must not hard-code the current upstream package version either. Read
  `upstream/sysml-2ls/packages/syside-languageserver/package.json` or call
  `getVersionInfo()` so submodule updates do not create stale assertions.
- `/v1/version` service version precedence is:
  `SERVICE_VERSION` env override, then `VERSION`, then `package.json.version`,
  then `0.0.0`.
- Unknown placeholder env values such as `unknown` are treated as unset by the
  API metadata layer.
- `src/version.ts` intentionally checks both source-run and built-runtime paths:
  source runs use `../VERSION`, built Docker runtime falls back to
  `../../VERSION` from `dist/src/version.js`.
- Docker images must copy `VERSION` into the runtime image.

When bumping the service version:

1. Update `VERSION`.
2. Update `package.json.version` to the same value.
3. Run `pnpm run version:check`.
4. Update docs/examples only when they intentionally name the new release.
5. Use a Git tag exactly equal to `v$(cat VERSION)`.

## Release and Docker Publishing

The first public release is `v0.1.0` at commit
`71190071e66750185730fd3681fa1b1262a2a0df`.

Published image names:

- GHCR: `ghcr.io/hansbug/sysmlv2-ls-service`
- Docker Hub: `hansbug/sysmlv2-ls-service` for the current
  `DOCKERHUB_NAMESPACE=hansbug` repo variable. If the variable changes, update
  docs and smoke commands to match.

Release workflow facts:

- `.github/workflows/release.yml` runs on `v*` tag pushes and manual dispatch.
- Tag pushes always publish GHCR.
- Docker Hub tag publishing happens only when repo variable
  `PUBLISH_DOCKERHUB_ON_TAG` is `true`.
- Manual Docker Hub publishing requires both `push_image=true` and
  `publish_dockerhub=true`.
- `check_dockerhub_login=true` is a login smoke only; it must not push images.
- The release job validates the Git tag equals `v$(cat VERSION)`.
- Both GHCR and Docker Hub publish these tag forms on a release tag:
  `vX.Y.Z`, `X.Y.Z`, `latest`, and `sha-<short-commit>`.
- Build args must stamp service version, service revision, source repository,
  upstream package version, upstream submodule revision, upstream repository, and
  UTC build date into `/v1/version` and OCI labels.

Real release checklist:

```bash
pnpm run ci
pnpm run audit
gh pr list --repo HansBug/sysmlv2-ls-service --state open
gh variable set PUBLISH_DOCKERHUB_ON_TAG --repo HansBug/sysmlv2-ls-service --body true
git tag "v$(cat VERSION)"
git push origin "v$(cat VERSION)"
# Wait for Release Docker Image to succeed.
gh variable set PUBLISH_DOCKERHUB_ON_TAG --repo HansBug/sysmlv2-ls-service --body false
```

Before creating the tag, confirm `git tag --list "v$(cat VERSION)"` is empty and
`gh release view "v$(cat VERSION)" --repo HansBug/sysmlv2-ls-service` does not
already resolve to an existing release.

After publishing, pull and run both registries before claiming success:

```bash
docker pull ghcr.io/hansbug/sysmlv2-ls-service:$(cat VERSION)
docker pull hansbug/sysmlv2-ls-service:$(cat VERSION)
```

Run container smoke checks for each published image:

- `GET /healthz`
- `GET /v1/version`
- `POST /v1/validate` with `package Demo { part def Vehicle; }`

Confirm `/v1/version` reports:

- `service.version == VERSION`
- `service.revision == release commit`
- upstream `sysml-2ls` package version and submodule revision
- Node.js runtime starts with `v24.`

Create or update the GitHub Release after the workflow succeeds. Include the
image names, quick `docker run` commands, release commit, upstream version, and
verification evidence. Never include secrets in release notes.

## Security and Dependency Hygiene

Security-sensitive facts:

- Docker Hub credentials live in GitHub repo variables/secrets:
  `DOCKERHUB_NAMESPACE`, `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
- Never print, commit, or echo Docker Hub tokens or other credentials.
- `PUBLISH_DOCKERHUB_ON_TAG` should normally be `false`; set it to `true` only
  for an intentional tag release, then restore it to `false`.
- If an automated release script sets `PUBLISH_DOCKERHUB_ON_TAG=true`, use a
  trap/finally-style cleanup so the variable is restored to `false` after
  success, failure, or interruption.
- GHCR publishing uses the built-in `GITHUB_TOKEN` with `packages: write`.

Before claiming a task ready, check:

```bash
pnpm run audit
gh pr list --repo HansBug/sysmlv2-ls-service --state open --json number,title,headRefName,author,createdAt
gh api repos/HansBug/sysmlv2-ls-service/dependabot/alerts --paginate --jq '[.[] | select(.state=="open")] | length'
gh api repos/HansBug/sysmlv2-ls-service/code-scanning/alerts --paginate --jq '[.[] | select(.state=="open")] | length'
gh api repos/HansBug/sysmlv2-ls-service/secret-scanning/alerts --paginate --jq '[.[] | select(.state=="open")] | length'
```

Treat new dependency update PRs as part of the current work when the user asks
for a ready release or security-clean repo. Resolve Dependabot PRs by reading the
diff, running CI/audit, and verifying no alerts remain.

## Upstream `sysml-2ls` Rules

- Do not edit files under `upstream/sysml-2ls` unless the task explicitly asks
  for an upstream fork patch.
- If updating the submodule, record the old and new upstream commit and rerun
  `pnpm run build:upstream`, `pnpm run ci`, Docker smoke, and diagnostics
  examples.
- Upstream `sysml-2ls` currently provides syntax, linking, and semantic
  validation through Langium/Chevrotain. Do not describe it as ANTLR-based.
- The upstream package version currently observed for the release is `0.9.1`.
  Recompute it from
  `upstream/sysml-2ls/packages/syside-languageserver/package.json`; do not rely
  on memory.
- State-machine validators such as `validateState*`, `validateTransition*`,
  `validateTriggerInvocationAction*`, and `validateExhibitStateUsageReference`
  are structural SysML checks. Do not market them as full model checking.

## Diagnostics Guidance

The diagnostics inventory in `README.md` is the user-facing reference. Keep it
in sync when changing normalization, examples, or upstream versions.

Diagnostics come from two layers:

- Langium/Chevrotain document diagnostics: lexing, parsing, linking.
- `sysml-2ls` SysML/KerML semantic validators: model-level constraints.

Implementation rules:

- Preserve diagnostic URI, severity, source, code, message, and range when
  available.
- Do not parse human-readable error text when a structured diagnostic field is
  available.
- Unknown diagnostic codes should remain visible; do not silently drop them.
- If changing diagnostic categorization in README, use real examples or tests.
- Parser and lexer errors must still be reported when semantic checks are
  disabled.

## Testing and Verification Gates

For normal code changes, run:

```bash
pnpm run format:check
pnpm run docs:check
pnpm run ci
pnpm run audit
```

For Python client changes, additionally run:

```bash
python -m pip install -e "clients/python[test]"
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
cd clients/python
python -m coverage run --branch -m pytest
python -m coverage report --fail-under=100
```

For Docker, release, version, dependency, or runtime-path changes, additionally
run a stamped Docker build and smoke it:

```bash
docker build -t sysmlv2-ls-service:local \
  --build-arg SERVICE_VERSION="$(cat VERSION)" \
  --build-arg SERVICE_REVISION="$(git rev-parse HEAD)" \
  --build-arg SOURCE_REPOSITORY=https://github.com/HansBug/sysmlv2-ls-service \
  --build-arg UPSTREAM_SYSML_2LS_VERSION="$(node -p 'require("./upstream/sysml-2ls/packages/syside-languageserver/package.json").version')" \
  --build-arg UPSTREAM_SYSML_2LS_REVISION="$(git -C upstream/sysml-2ls rev-parse HEAD)" \
  --build-arg UPSTREAM_SYSML_2LS_REPOSITORY=https://github.com/sensmetry/sysml-2ls \
  --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  .
```

Run container smoke on a random host port if `3000` is occupied. Do not kill
unrelated user containers or services just to free port `3000`.

Tests should cover:

- At least one valid SysML model with no diagnostics.
- Invalid syntax producing parser diagnostics.
- Invalid linking/semantic cases producing normalized diagnostics.
- Multi-file request behavior when imports are involved.
- Request validation failures such as duplicate canonical URIs and size limits.
- Timeout behavior for long-running validation.
- `/v1/version` env override and fallback behavior.

## Documentation Rules

- Keep `README.md` as the user-facing operational guide.
- Keep this file as the automation-agent operating contract.
- When changing public behavior, update README examples and tests in the same
  change.
- Python example docs must show both the command and representative output for a
  broken SysML example.
- If documenting a published image tag, verify the tag actually exists by
  pulling it.
- Avoid dynamic process ledgers in repo files. Use GitHub PR/release comments
  for transient status; repo docs should contain durable rules and facts.

## Git and Worktree Rules

- The worktree may be dirty. Never revert user changes unless explicitly asked.
- Before committing, inspect `git status --short`, staged diff, and relevant
  generated files.
- Do not use destructive commands such as `git reset --hard` or
  `git checkout --` unless the user explicitly asks.
- Keep commits scoped and reviewable.
- For release work, ensure `git status --short --ignored=no` is clean at the end.

## Multi-Agent Review Pattern

For release, security, or broad behavior changes, use independent adversarial
review when practical:

- One Codex reviewer/subagent.
- One `claude -p` reviewer when Claude CLI is available.
- One `codex-deepseek exec` reviewer when available.

Check that optional reviewer CLIs are on `PATH` before invoking them. If a
reviewer CLI is unavailable or unauthenticated, record that validation gap and
continue with the available reviewers rather than blocking forever.

Reviewer prompts should forbid sub-subagents, set a concrete time limit, and ask
for C/I/M findings:

- Critical: must block release or merge.
- Important: must be fixed before claiming ready.
- Minor: useful but non-blocking; fix opportunistically if cheap.

After review, the main agent owns integration and verification. Fix all C/I
findings, rerun the relevant verification, and only then report ready.

## Review Severity

- Critical: service cannot build, run, validate, or Dockerize; release publishes
  broken/mis-tagged images; API contract returns misleading success; unsafe
  execution; secrets leak; submodule is not reproducible.
- Important: missing CI coverage for a core path; version metadata can drift;
  Docker Hub/GHCR publishing gate is unsafe; poor diagnostic normalization;
  request isolation issues; README setup/release docs would mislead a user.
- Minor: naming, formatting, optional ergonomics, non-blocking docs polish, or
  follow-up improvements that do not affect correctness or release safety.
