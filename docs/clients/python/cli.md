# Python CLI

The `sysmlv2sl` CLI uses Click command groups. Every command and subcommand supports both `--help` and `-h`, and the help text is designed for humans and automation agents.

## Global options

```bash
sysmlv2sl --help
sysmlv2sl -h
sysmlv2sl --version
sysmlv2sl -v
```

Top-level `-v/--version` prints the Python client version only. The `version` subcommand calls the service and prints client plus service/upstream/build metadata.

| Option       | Environment variable | Meaning                                                |
| ------------ | -------------------- | ------------------------------------------------------ |
| `--base-url` | `SYSMLV2LS_URL`      | Service root URL. Defaults to `http://127.0.0.1:3000`. |
| `--timeout`  | `SYSMLV2LS_TIMEOUT`  | HTTP timeout in seconds.                               |
| `--json`     | n/a                  | Emit service DTO JSON instead of compact text.         |
| `--pretty`   | n/a                  | Indent JSON when `--json` is set.                      |

## Metadata commands

```bash
sysmlv2sl health
sysmlv2sl capabilities
sysmlv2sl version
sysmlv2sl --json --pretty version
```

`capabilities` is the easiest CLI way to inspect effective service-owned limits:

```bash
sysmlv2sl --json capabilities | jq '.limits'
```

## Validation commands

```bash
sysmlv2sl validate text 'package Demo { part def Vehicle; }'
cat demo.sysml | sysmlv2sl validate text --stdin --uri memory:///demo.sysml
sysmlv2sl validate text --file demo.sysml --validation-checks none
sysmlv2sl validate files models/a.sysml models/b.sysml
sysmlv2sl validate directory models --include '**/*.sysml' --exclude 'vendor/**'
```

Validation subcommands share these options:

| Option                | Values           | Notes                                                              |
| --------------------- | ---------------- | ------------------------------------------------------------------ |
| `--standard-library`  | `none`           | Mirrors service support.                                           |
| `--validation-checks` | `all`, `none`    | `none` skips semantic checks only.                                 |
| `--language`          | `sysml`, `kerml` | Explicit language override.                                        |
| `--no-client-limits`  | flag             | Skip client-side service-limit preflight.                          |
| `--limits`            | `auto`, `none`   | Use capabilities limits automatically or skip known client limits. |

## Directory command ergonomics

`validate directory` recursively includes `**/*.sysml` by default, excludes nothing, skips symlinks, and sends root-relative memory URIs:

```bash
sysmlv2sl validate directory .
```

Useful variants:

```bash
# Include both SysML and KerML files.
sysmlv2sl validate directory models --include '**/*.sysml' --include '**/*.kerml'

# Send absolute file paths instead of memory URIs.
sysmlv2sl validate directory models --uri-scheme file

# Prefix memory URIs with the directory root name.
sysmlv2sl validate directory models --absolute-uris

# Follow symlinks only when targets remain inside the root.
sysmlv2sl validate directory models --follow-symlinks
```

## Exit codes

| Exit code | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| `0`       | Command succeeded and validation `ok=true` when applicable.                                       |
| `1`       | Validation request succeeded but service returned `ok=false`.                                     |
| `2`       | Click usage error, such as invalid options.                                                       |
| `3`       | Connection, HTTP service error, malformed response, directory error, or client preflight failure. |

## Generated help reference

The generated [CLI reference](../../generated/cli/index.md) captures `sysmlv2sl --help` and every subcommand help output from the installed package. Regenerate it with `pnpm run docs:generate:cli` after CLI behavior changes.
