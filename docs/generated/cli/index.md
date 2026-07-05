# sysmlv2sl CLI reference

This page is generated from the installed `sysmlv2sl` Click command. Regenerate it with `pnpm run docs:generate:cli` after changing CLI behavior or help text.

## Top-level help

```console
$ sysmlv2sl --help
Usage: sysmlv2sl [OPTIONS] COMMAND [ARGS]...

  SysML v2 language-service client.

  Use subcommands to inspect service metadata or validate SysML/KerML input.
  Global --base-url and --timeout can also come from SYSMLV2LS_URL and
  SYSMLV2LS_TIMEOUT. Use --json for machine-readable output.

  Examples:
    sysmlv2sl health
    sysmlv2sl --base-url http://127.0.0.1:3000 version
    sysmlv2sl validate directory . --include '**/*.sysml'

Options:
  --base-url TEXT  Service root URL. Reverse-proxy path prefixes are allowed.
                   [env var: SYSMLV2LS_URL; default: http://127.0.0.1:3000]
  --timeout FLOAT  HTTP request timeout in seconds.  [env var:
                   SYSMLV2LS_TIMEOUT; default: 30.0]
  --json           Print service DTO JSON.
  --pretty         Pretty-print JSON output when --json is set.
  -v, --version    Show the version and exit.
  -h, --help       Show this message and exit.

Commands:
  capabilities  Show service capabilities.
  health        Check service liveness.
  validate      Validate SysML/KerML input.
  version       Show client and service version metadata.
```

## Version flag

```console
$ sysmlv2sl --version
sysmlv2slclient 0.1.0
```

## Health

```console
$ sysmlv2sl health --help
Usage: sysmlv2sl health [OPTIONS]

  Check service liveness.

  Prints a compact status by default. Use --json on the top-level command to
  emit the raw /healthz DTO for scripts and LLM agents.

Options:
  -h, --help  Show this message and exit.
```

## Capabilities

```console
$ sysmlv2sl capabilities --help
Usage: sysmlv2sl capabilities [OPTIONS]

  Show service capabilities.

  The output includes supported languages, validation modes, standard-library
  modes, and effective service-owned request limits. Disabled limits appear as
  null in JSON output.

Options:
  -h, --help  Show this message and exit.
```

## Version

```console
$ sysmlv2sl version --help
Usage: sysmlv2sl version [OPTIONS]

  Show client and service version metadata.

  Unlike top-level -v/--version, this command calls /v1/version and prints
  both the Python client version and the running service/upstream/build
  metadata.

Options:
  -h, --help  Show this message and exit.
```

## Validate

```console
$ sysmlv2sl validate --help
Usage: sysmlv2sl validate [OPTIONS] COMMAND [ARGS]...

  Validate SysML/KerML input.

  Validation failures are service diagnostics, not CLI failures: the command
  prints diagnostics and exits 1 when validation ok=false. CLI usage errors
  exit 2. Connection, HTTP, malformed-response, directory, and client
  preflight errors exit 3.

Options:
  -h, --help  Show this message and exit.

Commands:
  directory  Validate files discovered under a directory root.
  files      Validate multiple local files in one request-local workspace.
  text       Validate one text document.
```

## Validate text

```console
$ sysmlv2sl validate text --help
Usage: sysmlv2sl validate text [OPTIONS] [TEXT_VALUE]

  Validate one text document.

  Provide exactly one source: positional TEXT, --stdin, or --file. When --file
  is used without --uri or --path, the absolute file path is sent to the
  service.

  Examples:
    sysmlv2sl validate text 'package Demo { part def Vehicle; }'
    cat demo.sysml | sysmlv2sl validate text --stdin --uri memory:///demo.sysml
    sysmlv2sl validate text --file demo.sysml --validation-checks none

Options:
  --stdin                         Read document text from standard input.
  --file FILE                     Read document text from a local file.
  --uri TEXT                      Document URI to send with the text.
  --path TEXT                     Document path to send with the text.
  --encoding TEXT                 File input encoding.  [default: utf-8]
  --encoding-errors TEXT          File decoding error handler.  [default:
                                  strict]
  --standard-library [none]       Service standard-library mode.  [default:
                                  none]
  --validation-checks [all|none]  Use 'none' to skip semantic checks while
                                  preserving lexer/parser diagnostics.
                                  [default: all]
  --language [sysml|kerml]        Explicit language for submitted files.
  --no-client-limits              Skip client-side service-limit preflight.
                                  Required enum and path checks remain.
  --limits [auto|none]            Use capabilities limits automatically, or
                                  skip known client limits with 'none'.
                                  [default: auto]
  -h, --help                      Show this message and exit.
```

## Validate files

```console
$ sysmlv2sl validate files --help
Usage: sysmlv2sl validate files [OPTIONS] [PATHS]...

  Validate multiple local files in one request-local workspace.

  Memory URI mode generates stable memory:/// URIs from the common parent of
  the provided paths. File URI mode sends absolute file paths. Use --json on
  the top-level command for the full validate DTO.

  Example:
    sysmlv2sl validate files models/a.sysml models/b.sysml

Options:
  --uri-scheme [memory|file]      Send generated memory URIs or absolute file
                                  paths.  [default: memory]
  --relative-uris / --absolute-uris
                                  Use root-relative memory URIs, or prefix
                                  memory URIs with the common root name.
                                  [default: relative-uris]
  --encoding TEXT                 File input encoding.  [default: utf-8]
  --encoding-errors TEXT          File decoding error handler.  [default:
                                  strict]
  --standard-library [none]       Service standard-library mode.  [default:
                                  none]
  --validation-checks [all|none]  Use 'none' to skip semantic checks while
                                  preserving lexer/parser diagnostics.
                                  [default: all]
  --language [sysml|kerml]        Explicit language for submitted files.
  --no-client-limits              Skip client-side service-limit preflight.
                                  Required enum and path checks remain.
  --limits [auto|none]            Use capabilities limits automatically, or
                                  skip known client limits with 'none'.
                                  [default: auto]
  -h, --help                      Show this message and exit.
```

## Validate directory

```console
$ sysmlv2sl validate directory --help
Usage: sysmlv2sl validate directory [OPTIONS] ROOT

  Validate files discovered under a directory root.

  By default this recursively includes **/*.sysml, excludes nothing, does not
  follow symlinks, and sends memory:/// URIs relative to ROOT. Include/exclude
  patterns must stay relative to ROOT.

  Examples:
    sysmlv2sl validate directory .
    sysmlv2sl validate directory . --include '**/*.sysml' --exclude 'vendor/**'
    sysmlv2sl validate directory . --uri-scheme file

Options:
  --include TEXT                  Relative glob include pattern. Repeat for
                                  more patterns.  [default: **/*.sysml]
  --exclude TEXT                  Relative glob exclude pattern. Repeat for
                                  more patterns.
  --uri-scheme [memory|file]      Use generated memory URIs or absolute file
                                  paths.  [default: memory]
  --relative-uris / --absolute-uris
                                  Use root-relative memory URIs. File mode
                                  always sends absolute paths.  [default:
                                  relative-uris]
  --encoding TEXT                 File input encoding.  [default: utf-8]
  --encoding-errors TEXT          File decoding error handler.  [default:
                                  strict]
  --follow-symlinks               Follow symlinks that stay inside ROOT; loops
                                  and escapes are rejected.
  --standard-library [none]       Service standard-library mode.  [default:
                                  none]
  --validation-checks [all|none]  Use 'none' to skip semantic checks while
                                  preserving lexer/parser diagnostics.
                                  [default: all]
  --language [sysml|kerml]        Explicit language for submitted files.
  --no-client-limits              Skip client-side service-limit preflight.
                                  Required enum and path checks remain.
  --limits [auto|none]            Use capabilities limits automatically, or
                                  skip known client limits with 'none'.
                                  [default: auto]
  -h, --help                      Show this message and exit.
```
