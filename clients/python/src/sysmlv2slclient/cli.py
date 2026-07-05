"""
Click command-line interface for the Python client.

The module exposes the ``sysmlv2sl`` console script. It keeps command behavior
aligned with :class:`sysmlv2slclient.client.SysMLV2LSClient` and focuses on
human-friendly help, stable exit codes, and optional JSON output for automation.

The module contains:

* :func:`cli` - top-level Click command group.
* :func:`validate` - validation command group with text, files, and directory
  subcommands.

Example::

    $ sysmlv2sl --version
    $ sysmlv2sl validate text 'package Demo {}'
"""

import json
import os
from pathlib import Path
from urllib.parse import quote

import click

from ._version import __version__
from .client import SysMLV2LSClient
from .errors import SysMLClientError
from .models import SysMLFile

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 100,
}
DEFAULT_BASE_URL = "http://127.0.0.1:3000"


class SysMLCLIError(click.ClickException):
    """
    Click exception used for SDK/runtime failures.

    :param message: Error message printed by Click.
    :type message: str

    Example::

        >>> SysMLCLIError("offline").exit_code
        3
    """

    exit_code = 3


def _client_version_dict():
    return {"name": "sysmlv2slclient", "version": __version__}


def _json_echo(ctx, payload):
    indent = 2 if ctx.obj["pretty"] else None
    click.echo(json.dumps(payload, indent=indent, ensure_ascii=False))


def _emit(ctx, payload, lines):
    if ctx.obj["output_json"]:
        _json_echo(ctx, payload)
        return
    for line in lines:
        click.echo(line)


def _limits_arg(value):
    if value == "none":
        return None
    return "auto"


def _make_client(ctx, enforce_client_limits=True, limits="auto"):
    return SysMLV2LSClient(
        ctx.obj["base_url"],
        timeout=ctx.obj["timeout"],
        enforce_client_limits=enforce_client_limits,
        limits=limits,
    )


def _validate_client(ctx):
    options = ctx.obj["validate_options"]
    return _make_client(
        ctx,
        enforce_client_limits=not options["no_client_limits"],
        limits=_limits_arg(options["limits"]),
    )


def _call_client(call):
    try:
        return call()
    except SysMLClientError as error:
        raise SysMLCLIError(str(error))


def _validation_options(ctx):
    return ctx.obj["validate_options"]


def _store_validation_options(
    ctx,
    standard_library,
    validation_checks,
    language,
    no_client_limits,
    limits,
):
    ctx.obj["validate_options"] = {
        "standard_library": standard_library,
        "validation_checks": validation_checks,
        "language": language,
        "no_client_limits": no_client_limits,
        "limits": limits,
    }


def _validation_options_decorator(function):
    function = click.option(
        "--limits",
        type=click.Choice(["auto", "none"]),
        default="auto",
        show_default=True,
        help="Use capabilities limits automatically, or skip known client limits with 'none'.",
    )(function)
    function = click.option(
        "--no-client-limits",
        is_flag=True,
        help="Skip client-side service-limit preflight. Required enum and path checks remain.",
    )(function)
    function = click.option(
        "--language",
        type=click.Choice(["sysml", "kerml"]),
        default=None,
        help="Explicit language for submitted files.",
    )(function)
    function = click.option(
        "--validation-checks",
        type=click.Choice(["all", "none"]),
        default="all",
        show_default=True,
        help="Use 'none' to skip semantic checks while preserving lexer/parser diagnostics.",
    )(function)
    function = click.option(
        "--standard-library",
        type=click.Choice(["none"]),
        default="none",
        show_default=True,
        help="Service standard-library mode.",
    )(function)
    return function


def _validation_kwargs(ctx):
    options = _validation_options(ctx)
    return {
        "standard_library": options["standard_library"],
        "validation_checks": options["validation_checks"],
    }


def _diagnostic_line(diagnostic):
    position = diagnostic.range.start
    location = "%s:%s:%s" % (diagnostic.uri, position.line, position.character)
    return "%s %s %s" % (diagnostic.severity, location, diagnostic.message)


def _emit_validation_result(ctx, result):
    lines = [
        "ok: %s" % str(result.ok).lower(),
        "files: %s" % len(result.files),
        "diagnostics: %s" % len(result.diagnostics),
    ]
    for diagnostic in result.diagnostics:
        lines.append(_diagnostic_line(diagnostic))
    _emit(ctx, result.to_dict(), lines)
    if not result.ok:
        ctx.exit(1)


def _read_text_file(path, encoding, encoding_errors):
    try:
        return Path(path).read_text(encoding=encoding, errors=encoding_errors)
    except UnicodeDecodeError as error:
        raise SysMLCLIError("Cannot decode %s: %s" % (path, error))
    except OSError as error:
        raise SysMLCLIError("Cannot read %s: %s" % (path, error))


def _memory_uri(root, resolved_path, relative_uris):
    rel_posix = Path(os.path.relpath(str(resolved_path), str(root))).as_posix()
    segments = rel_posix.split("/")
    encoded = "/".join(quote(segment, safe="") for segment in segments)
    if relative_uris:
        return "memory:///%s" % encoded
    root_name = quote(root.name or "workspace", safe="")
    return "memory:///%s/%s" % (root_name, encoded)


def _load_cli_files(paths, uri_scheme, relative_uris, language, encoding, encoding_errors):
    resolved_paths = []
    parent_paths = []
    for path in paths:
        resolved_path = Path(path).resolve()
        resolved_paths.append(resolved_path)
        parent_paths.append(str(resolved_path.parent))
    root = Path(os.path.commonpath(parent_paths))
    files = []
    for input_path, resolved_path in zip(paths, resolved_paths):
        text = _read_text_file(input_path, encoding, encoding_errors)
        if uri_scheme == "file":
            files.append(SysMLFile(path=str(resolved_path), text=text, language=language))
        else:
            files.append(
                SysMLFile(
                    uri=_memory_uri(root, resolved_path, relative_uris),
                    text=text,
                    language=language,
                )
            )
    return files


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="""SysML v2 language-service client.

Use subcommands to inspect service metadata or validate SysML/KerML input.
Global --base-url and --timeout can also come from SYSMLV2LS_URL and
SYSMLV2LS_TIMEOUT. Use --json for machine-readable output.

\b
Examples:
  sysmlv2sl health
  sysmlv2sl --base-url http://127.0.0.1:3000 version
  sysmlv2sl validate directory . --include '**/*.sysml'
""",
)
@click.option(
    "--base-url",
    envvar="SYSMLV2LS_URL",
    default=DEFAULT_BASE_URL,
    show_default=True,
    show_envvar=True,
    help="Service root URL. Reverse-proxy path prefixes are allowed.",
)
@click.option(
    "--timeout",
    envvar="SYSMLV2LS_TIMEOUT",
    default=30.0,
    show_default=True,
    show_envvar=True,
    type=float,
    help="HTTP request timeout in seconds.",
)
@click.option("--json", "output_json", is_flag=True, help="Print service DTO JSON.")
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty-print JSON output when --json is set.",
)
@click.version_option(__version__, "-v", "--version", message="sysmlv2slclient %(version)s")
@click.pass_context
def cli(ctx, base_url, timeout, output_json, pretty):
    """
    Dispatch the top-level ``sysmlv2sl`` command group.

    :param ctx: Click command context.
    :type ctx: click.Context
    :param base_url: Service root URL.
    :type base_url: str
    :param timeout: HTTP timeout in seconds.
    :type timeout: float
    :param output_json: Whether output should be machine-readable JSON.
    :type output_json: bool
    :param pretty: Whether JSON output should be indented.
    :type pretty: bool
    :return: ``None``.
    :rtype: None

    Example::

        $ sysmlv2sl --base-url http://127.0.0.1:3000 health
    """

    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "base_url": base_url,
            "timeout": timeout,
            "output_json": output_json,
            "pretty": pretty,
        }
    )


@cli.command(
    context_settings=CONTEXT_SETTINGS,
    help="""Check service liveness.

Prints a compact status by default. Use --json on the top-level command to
emit the raw /healthz DTO for scripts and LLM agents.
""",
)
@click.pass_context
def health(ctx):
    """
    Print service health.

    :param ctx: Click command context.
    :type ctx: click.Context
    :return: ``None``.
    :rtype: None
    :raises SysMLCLIError: If the service call fails.

    Example::

        $ sysmlv2sl health
    """

    result = _call_client(lambda: _make_client(ctx).health())
    _emit(
        ctx,
        result.to_dict(),
        [
            "ok: %s" % str(result.ok).lower(),
            "service: %s" % result.service,
            "version: %s" % result.version,
        ],
    )


@cli.command(
    context_settings=CONTEXT_SETTINGS,
    help="""Show service capabilities.

The output includes supported languages, validation modes, standard-library
modes, and effective service-owned request limits. Disabled limits appear as
null in JSON output.
""",
)
@click.pass_context
def capabilities(ctx):
    """
    Print service capabilities and effective limits.

    :param ctx: Click command context.
    :type ctx: click.Context
    :return: ``None``.
    :rtype: None
    :raises SysMLCLIError: If the service call fails.

    Example::

        $ sysmlv2sl --json capabilities
    """

    result = _call_client(lambda: _make_client(ctx).capabilities())
    language_ids = ", ".join(language.id for language in result.languages)
    _emit(
        ctx,
        result.to_dict(),
        [
            "languages: %s" % language_ids,
            "validationChecks: %s" % ", ".join(result.validation_checks),
            "standardLibrary: %s" % ", ".join(result.standard_library),
            "maxFiles: %s" % result.limits.validate.max_files,
            "bodyLimitBytes: %s" % result.limits.http.body_limit_bytes,
        ],
    )


@cli.command(
    context_settings=CONTEXT_SETTINGS,
    help="""Show client and service version metadata.

Unlike top-level -v/--version, this command calls /v1/version and prints both
the Python client version and the running service/upstream/build metadata.
""",
)
@click.pass_context
def version(ctx):
    """
    Print client and service version metadata.

    :param ctx: Click command context.
    :type ctx: click.Context
    :return: ``None``.
    :rtype: None
    :raises SysMLCLIError: If the service call fails.

    Example::

        $ sysmlv2sl version
    """

    result = _call_client(lambda: _make_client(ctx).version())
    payload = {"client": _client_version_dict()}
    payload.update(result.to_dict())
    _emit(
        ctx,
        payload,
        [
            "client: sysmlv2slclient %s" % __version__,
            "service: %s %s" % (result.service.name, result.service.version),
            "serviceRevision: %s" % result.service.revision,
            "upstreamSysML2LS: %s" % result.upstream.sysml2ls.version,
            "node: %s" % result.build.node_version,
        ],
    )


@cli.group(
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    help="""Validate SysML/KerML input.

Validation failures are service diagnostics, not CLI failures: the command
prints diagnostics and exits 1 when validation ok=false. CLI usage errors exit
2. Connection, HTTP, malformed-response, directory, and client preflight errors
exit 3.
""",
)
@click.pass_context
def validate(ctx):
    """
    Dispatch validation subcommands.

    :param ctx: Click command context.
    :type ctx: click.Context
    :return: ``None``.
    :rtype: None

    Example::

        $ sysmlv2sl validate text 'package Demo {}'
    """

    ctx.obj.setdefault("validate_options", {})


@validate.command(
    "text",
    context_settings=CONTEXT_SETTINGS,
    help="""Validate one text document.

Provide exactly one source: positional TEXT, --stdin, or --file. When --file is
used without --uri or --path, the absolute file path is sent to the service.

\b
Examples:
  sysmlv2sl validate text 'package Demo { part def Vehicle; }'
  cat demo.sysml | sysmlv2sl validate text --stdin --uri memory:///demo.sysml
  sysmlv2sl validate text --file demo.sysml --validation-checks none
""",
)
@click.argument("text_value", required=False)
@click.option(
    "--stdin", "read_stdin", is_flag=True, help="Read document text from standard input."
)
@click.option(
    "--file",
    "input_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Read document text from a local file.",
)
@click.option("--uri", help="Document URI to send with the text.")
@click.option("--path", "document_path", help="Document path to send with the text.")
@click.option("--encoding", default="utf-8", show_default=True, help="File input encoding.")
@click.option(
    "--encoding-errors",
    default="strict",
    show_default=True,
    help="File decoding error handler.",
)
@_validation_options_decorator
@click.pass_context
def validate_text(
    ctx,
    text_value,
    read_stdin,
    input_file,
    uri,
    document_path,
    encoding,
    encoding_errors,
    standard_library,
    validation_checks,
    language,
    no_client_limits,
    limits,
):
    """
    Validate one text document from an argument, stdin, or a file.

    :param ctx: Click command context.
    :type ctx: click.Context
    :param text_value: Optional positional document text.
    :type text_value: str, optional
    :param read_stdin: Whether to read document text from stdin.
    :type read_stdin: bool
    :param input_file: Optional local input file path.
    :type input_file: str, optional
    :param uri: Optional document URI.
    :type uri: str, optional
    :param document_path: Optional document path.
    :type document_path: str, optional
    :param encoding: File input encoding.
    :type encoding: str
    :param encoding_errors: File decoding error handler.
    :type encoding_errors: str
    :param standard_library: Service standard-library mode.
    :type standard_library: str
    :param validation_checks: Validation-check mode.
    :type validation_checks: str
    :param language: Optional explicit language.
    :type language: str, optional
    :param no_client_limits: Whether to skip client limit preflight.
    :type no_client_limits: bool
    :param limits: Client limit mode.
    :type limits: str
    :return: ``None``.
    :rtype: None
    :raises click.UsageError: If the user provides zero or multiple sources.
    :raises SysMLCLIError: If file reading or the service call fails.

    Example::

        $ sysmlv2sl validate text --stdin --uri memory:///demo.sysml
    """

    _store_validation_options(
        ctx,
        standard_library,
        validation_checks,
        language,
        no_client_limits,
        limits,
    )
    source_count = sum(
        1 for provided in (text_value is not None, read_stdin, input_file is not None) if provided
    )
    if source_count != 1:
        raise click.UsageError("Provide exactly one of TEXT, --stdin, or --file.")
    if read_stdin:
        text = click.get_text_stream("stdin").read()
    elif input_file is not None:
        text = _read_text_file(input_file, encoding, encoding_errors)
        if uri is None and document_path is None:
            document_path = str(Path(input_file).resolve())
    else:
        text = text_value
    options = _validation_options(ctx)
    result = _call_client(
        lambda: _validate_client(ctx).validate_text(
            text,
            uri=uri,
            path=document_path,
            language=options["language"],
            **_validation_kwargs(ctx),
        )
    )
    _emit_validation_result(ctx, result)


@validate.command(
    "files",
    context_settings=CONTEXT_SETTINGS,
    help="""Validate multiple local files in one request-local workspace.

Memory URI mode generates stable memory:/// URIs from the common parent of the
provided paths. File URI mode sends absolute file paths. Use --json on the
top-level command for the full validate DTO.

\b
Example:
  sysmlv2sl validate files models/a.sysml models/b.sysml
""",
)
@click.argument("paths", nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--uri-scheme",
    type=click.Choice(["memory", "file"]),
    default="memory",
    show_default=True,
    help="Send generated memory URIs or absolute file paths.",
)
@click.option(
    "--relative-uris/--absolute-uris",
    default=True,
    show_default=True,
    help="Use root-relative memory URIs, or prefix memory URIs with the common root name.",
)
@click.option("--encoding", default="utf-8", show_default=True, help="File input encoding.")
@click.option(
    "--encoding-errors",
    default="strict",
    show_default=True,
    help="File decoding error handler.",
)
@_validation_options_decorator
@click.pass_context
def validate_files(
    ctx,
    paths,
    uri_scheme,
    relative_uris,
    encoding,
    encoding_errors,
    standard_library,
    validation_checks,
    language,
    no_client_limits,
    limits,
):
    """
    Validate multiple local files in one request.

    :param ctx: Click command context.
    :type ctx: click.Context
    :param paths: Local file paths.
    :type paths: tuple[str, ...]
    :param uri_scheme: ``"memory"`` or ``"file"``.
    :type uri_scheme: str
    :param relative_uris: Whether generated memory URIs are relative.
    :type relative_uris: bool
    :param encoding: File input encoding.
    :type encoding: str
    :param encoding_errors: File decoding error handler.
    :type encoding_errors: str
    :param standard_library: Service standard-library mode.
    :type standard_library: str
    :param validation_checks: Validation-check mode.
    :type validation_checks: str
    :param language: Optional explicit language.
    :type language: str, optional
    :param no_client_limits: Whether to skip client limit preflight.
    :type no_client_limits: bool
    :param limits: Client limit mode.
    :type limits: str
    :return: ``None``.
    :rtype: None
    :raises click.UsageError: If no file paths are provided.
    :raises SysMLCLIError: If file reading or the service call fails.

    Example::

        $ sysmlv2sl validate files a.sysml b.sysml
    """

    _store_validation_options(
        ctx,
        standard_library,
        validation_checks,
        language,
        no_client_limits,
        limits,
    )
    if not paths:
        raise click.UsageError("Provide at least one file path.")
    options = _validation_options(ctx)
    files = _load_cli_files(
        paths,
        uri_scheme=uri_scheme,
        relative_uris=relative_uris,
        language=options["language"],
        encoding=encoding,
        encoding_errors=encoding_errors,
    )
    result = _call_client(
        lambda: _validate_client(ctx).validate_files(files, **_validation_kwargs(ctx))
    )
    _emit_validation_result(ctx, result)


@validate.command(
    "directory",
    context_settings=CONTEXT_SETTINGS,
    help="""Validate files discovered under a directory root.

By default this recursively includes **/*.sysml, excludes nothing, does not
follow symlinks, and sends memory:/// URIs relative to ROOT. Include/exclude
patterns must stay relative to ROOT.

\b
Examples:
  sysmlv2sl validate directory .
  sysmlv2sl validate directory . --include '**/*.sysml' --exclude 'vendor/**'
  sysmlv2sl validate directory . --uri-scheme file
""",
)
@click.argument("root", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--include",
    multiple=True,
    default=("**/*.sysml",),
    show_default=True,
    help="Relative glob include pattern. Repeat for more patterns.",
)
@click.option(
    "--exclude",
    multiple=True,
    default=(),
    help="Relative glob exclude pattern. Repeat for more patterns.",
)
@click.option(
    "--uri-scheme",
    type=click.Choice(["memory", "file"]),
    default="memory",
    show_default=True,
    help="Use generated memory URIs or absolute file paths.",
)
@click.option(
    "--relative-uris/--absolute-uris",
    default=True,
    show_default=True,
    help="Use root-relative memory URIs. File mode always sends absolute paths.",
)
@click.option("--encoding", default="utf-8", show_default=True, help="File input encoding.")
@click.option(
    "--encoding-errors",
    default="strict",
    show_default=True,
    help="File decoding error handler.",
)
@click.option(
    "--follow-symlinks",
    is_flag=True,
    help="Follow symlinks that stay inside ROOT; loops and escapes are rejected.",
)
@_validation_options_decorator
@click.pass_context
def validate_directory(
    ctx,
    root,
    include,
    exclude,
    uri_scheme,
    relative_uris,
    encoding,
    encoding_errors,
    follow_symlinks,
    standard_library,
    validation_checks,
    language,
    no_client_limits,
    limits,
):
    """
    Validate files discovered under a directory root.

    :param ctx: Click command context.
    :type ctx: click.Context
    :param root: Directory root.
    :type root: str
    :param include: Include glob patterns.
    :type include: tuple[str, ...]
    :param exclude: Exclude glob patterns.
    :type exclude: tuple[str, ...]
    :param uri_scheme: ``"memory"`` or ``"file"``.
    :type uri_scheme: str
    :param relative_uris: Whether generated memory URIs are relative.
    :type relative_uris: bool
    :param encoding: File input encoding.
    :type encoding: str
    :param encoding_errors: File decoding error handler.
    :type encoding_errors: str
    :param follow_symlinks: Whether to follow symlinks inside the root.
    :type follow_symlinks: bool
    :param standard_library: Service standard-library mode.
    :type standard_library: str
    :param validation_checks: Validation-check mode.
    :type validation_checks: str
    :param language: Optional explicit language.
    :type language: str, optional
    :param no_client_limits: Whether to skip client limit preflight.
    :type no_client_limits: bool
    :param limits: Client limit mode.
    :type limits: str
    :return: ``None``.
    :rtype: None
    :raises SysMLCLIError: If directory collection or the service call fails.

    Example::

        $ sysmlv2sl validate directory . --include '**/*.sysml'
    """

    _store_validation_options(
        ctx,
        standard_library,
        validation_checks,
        language,
        no_client_limits,
        limits,
    )
    options = _validation_options(ctx)
    result = _call_client(
        lambda: _validate_client(ctx).validate_directory(
            root,
            include=include,
            exclude=exclude,
            uri_scheme=uri_scheme,
            relative_uris=relative_uris if uri_scheme == "memory" else False,
            language=options["language"],
            encoding=encoding,
            encoding_errors=encoding_errors,
            follow_symlinks=follow_symlinks,
            **_validation_kwargs(ctx),
        )
    )
    _emit_validation_result(ctx, result)
