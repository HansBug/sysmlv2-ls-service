# Quickstart

This page validates that the repository, pinned upstream submodule, local Node.js toolchain, service, and optional Python client are usable for development.

## 1. Initialize the repository

```bash
git submodule update --init --recursive
corepack enable
pnpm install --frozen-lockfile
pnpm run build:upstream
```

`build:upstream` generates and builds the pinned `sysml-2ls` packages used by the adapter. If upstream artifacts are missing, the service and upstream inventory generation cannot run reliably.

## 2. Install documentation/client helpers

The service checks themselves are Node-based, but the full documentation gate
also regenerates Python CLI help and builds the MkDocs site. Install those
Python-side helpers before running `docs:check` in a clean checkout:

```bash
python -m pip install -r docs/requirements.txt
python -m pip install --no-build-isolation -e clients/python
```

Use `clients/python[test]` instead of `clients/python` when you also want to run
the Python client unit tests locally.

## 3. Run the service checks

```bash
pnpm run version:check
pnpm run format:check
pnpm run docs:check
pnpm run ci
pnpm run audit
```

`pnpm run ci` includes version consistency, TypeScript type checking, ESLint, JSDoc/TSDoc checks, coverage, build, and a service smoke start. `docs:check` is the full documentation gate and can take longer because it regenerates upstream inventory.

## 4. Start the development server

```bash
pnpm run dev
```

The default service root is `http://127.0.0.1:3000`. Keep this terminal open for the curl and Python examples below.

## 5. Validate one in-memory SysML file

```bash
curl -sS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///demo.sysml","text":"package Demo { part def Vehicle; }"}]}' \
  | jq
```

Expected shape:

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

`elapsedMs` varies by machine. Any `diagnostics` entry with severity `error`, or any lexer/parser error, makes `ok` false.

## 6. Exercise multi-file behavior

The service resolves imports only among files submitted in the same request. This example sends two memory documents as one request-local workspace:

```bash
curl -sS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data @- <<'JSON' | jq '.ok, .diagnostics'
{
  "files": [
    {
      "uri": "memory:///library.sysml",
      "text": "package Library { part def Vehicle; }"
    },
    {
      "uri": "memory:///model.sysml",
      "text": "package Model { public import Library::*; part car : Vehicle; }"
    }
  ]
}
JSON
```

Submit the same second file without `library.sysml` and it should produce a `linking-error` for the missing import or type.

## 7. Use the Python client and CLI

```bash
python -m pip install -e "clients/python[test]"
sysmlv2sl --version
sysmlv2sl --base-url http://127.0.0.1:3000 health
sysmlv2sl validate text 'package Demo { part def Vehicle; }'
```

For class-based use:

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)
print(result.ok)
```

## Troubleshooting

| Symptom                                    | Likely cause                                 | Fix                                                                                                       |
| ------------------------------------------ | -------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `Cannot find module syside-languageserver` | Upstream packages were not built.            | Run `git submodule update --init --recursive` and `pnpm run build:upstream`.                              |
| `pnpm install --frozen-lockfile` fails     | Lockfile and package metadata differ.        | Use `pnpm install` only when intentionally updating dependency metadata, then commit the lockfile change. |
| `validation_timeout` HTTP 503              | The service timeout wrapper expired.         | Increase or disable `VALIDATION_TIMEOUT_MS` for trusted workloads.                                        |
| Python CLI cannot connect                  | Service is not running or base URL is wrong. | Start `pnpm run dev` and pass `--base-url` or `SYSMLV2LS_URL`.                                            |
