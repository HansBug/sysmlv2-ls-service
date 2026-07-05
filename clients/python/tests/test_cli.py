import json

import pytest
from click.testing import CliRunner

import sysmlv2slclient.cli as cli_module
from sysmlv2slclient import (
    CapabilitiesResponse,
    HealthResponse,
    SysMLConnectionError,
    SysMLDirectoryError,
    ValidateResult,
    VersionResponse,
)


def health_body():
    return {"ok": True, "service": "svc", "version": "1"}


def capabilities_body():
    return {
        "languages": [{"id": "sysml", "extensions": [".sysml"]}],
        "validationChecks": ["all", "none"],
        "standardLibrary": ["none"],
        "limits": {
            "validate": {
                "maxFiles": 10,
                "maxFileTextBytes": 100,
                "maxTotalTextBytes": 1000,
                "validationTimeoutMs": 30000,
            },
            "http": {"bodyLimitBytes": 5000},
        },
    }


def version_body():
    return {
        "service": {
            "name": "svc",
            "version": "1",
            "revision": "abc",
            "sourceRepository": "repo",
        },
        "upstream": {
            "sysml2ls": {
                "version": "2",
                "revision": "def",
                "packageName": "pkg",
                "repository": "up",
            }
        },
        "build": {"date": "today", "nodeVersion": "v24.0.0"},
    }


def validate_body(ok=True):
    diagnostics = []
    if not ok:
        diagnostics.append(
            {
                "severity": "error",
                "source": "sysml",
                "message": "bad syntax",
                "uri": "memory:///bad.sysml",
                "range": {
                    "start": {"line": 1, "character": 2},
                    "end": {"line": 1, "character": 3},
                },
            }
        )
    return {
        "ok": ok,
        "diagnostics": diagnostics,
        "files": [
            {
                "uri": "memory:///demo.sysml",
                "language": "sysml",
                "parserErrors": 0 if ok else 1,
                "lexerErrors": 0,
                "diagnostics": len(diagnostics),
            }
        ],
        "meta": {
            "standardLibrary": "none",
            "validationChecks": "all",
            "elapsedMs": 1,
        },
    }


class FakeClient(object):
    instances = []
    validate_result = validate_body()
    directory_calls = []

    def __init__(self, base_url, timeout=30.0, enforce_client_limits=True, limits="auto"):
        self.base_url = base_url
        self.timeout = timeout
        self.enforce_client_limits = enforce_client_limits
        self.limits = limits
        self.calls = []
        FakeClient.instances.append(self)

    def health(self):
        self.calls.append(("health",))
        return HealthResponse.from_dict(health_body())

    def capabilities(self):
        self.calls.append(("capabilities",))
        return CapabilitiesResponse.from_dict(capabilities_body())

    def version(self):
        self.calls.append(("version",))
        return VersionResponse.from_dict(version_body())

    def validate_text(self, text, uri=None, path=None, language=None, **kwargs):
        self.calls.append(("validate_text", text, uri, path, language, kwargs))
        return ValidateResult.from_dict(FakeClient.validate_result)

    def validate_files(self, files, **kwargs):
        self.calls.append(("validate_files", files, kwargs))
        return ValidateResult.from_dict(FakeClient.validate_result)

    def validate_directory(self, path, **kwargs):
        self.calls.append(("validate_directory", path, kwargs))
        FakeClient.directory_calls.append((path, kwargs))
        return ValidateResult.from_dict(FakeClient.validate_result)


@pytest.fixture(autouse=True)
def fake_client(monkeypatch):
    FakeClient.instances = []
    FakeClient.validate_result = validate_body()
    FakeClient.directory_calls = []
    monkeypatch.setattr(cli_module, "SysMLV2LSClient", FakeClient)


def invoke(args, **kwargs):
    return CliRunner().invoke(cli_module.cli, args, **kwargs)


@pytest.mark.parametrize(
    "args",
    [
        ["-h"],
        ["health", "-h"],
        ["capabilities", "-h"],
        ["version", "-h"],
        ["validate", "-h"],
        ["validate", "text", "-h"],
        ["validate", "files", "-h"],
        ["validate", "directory", "-h"],
    ],
)
def test_help_aliases(args):
    result = invoke(args)
    assert result.exit_code == 0
    assert "Usage:" in result.output


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_top_level_version_flags(flag):
    result = invoke([flag])
    assert result.exit_code == 0
    assert result.output.strip().startswith("sysmlv2slclient ")


def test_health_capabilities_and_version_outputs_json_and_text():
    health = invoke(["--base-url", "http://svc.test/api", "--timeout", "2", "health"])
    assert health.exit_code == 0
    assert "ok: true" in health.output
    assert FakeClient.instances[-1].base_url == "http://svc.test/api"
    assert FakeClient.instances[-1].timeout == 2

    capabilities = invoke(["capabilities"])
    assert capabilities.exit_code == 0
    assert "languages: sysml" in capabilities.output

    version = invoke(["--json", "--pretty", "version"])
    assert version.exit_code == 0
    payload = json.loads(version.output)
    assert payload["client"]["name"] == "sysmlv2slclient"
    assert payload["service"]["revision"] == "abc"


def test_global_parameter_validation_is_click_usage_error():
    query = invoke(["--base-url", "http://svc.test?bad=true", "health"])
    assert query.exit_code == 2
    assert "must not include query or fragment" in query.output
    assert "Traceback" not in query.output

    no_host = invoke(["--base-url", "svc.test", "health"])
    assert no_host.exit_code == 2
    assert "must include scheme and host" in no_host.output
    assert "Traceback" not in no_host.output

    bad_timeout = invoke(["--timeout", "0", "health"])
    assert bad_timeout.exit_code == 2
    assert "must be a finite number greater than 0" in bad_timeout.output
    assert "Traceback" not in bad_timeout.output

    infinite_timeout = invoke(["--timeout", "inf", "health"])
    assert infinite_timeout.exit_code == 2
    assert "must be a finite number greater than 0" in infinite_timeout.output
    assert "Traceback" not in infinite_timeout.output

    nan_timeout = invoke(["--timeout", "nan", "health"])
    assert nan_timeout.exit_code == 2
    assert "must be a finite number greater than 0" in nan_timeout.output
    assert "Traceback" not in nan_timeout.output


def test_validate_text_sources_and_failure_exit(tmp_path):
    ok = invoke(["validate", "text", "package Demo {}", "--uri", "memory:///demo.sysml"])
    assert ok.exit_code == 0
    assert FakeClient.instances[-1].calls[-1][1] == "package Demo {}"

    stdin = invoke(["validate", "text", "--stdin"], input="package Demo {}")
    assert stdin.exit_code == 0
    assert FakeClient.instances[-1].calls[-1][1] == "package Demo {}"

    source = tmp_path / "demo.sysml"
    source.write_text("package Demo {}", encoding="utf-8")
    from_file = invoke(["validate", "text", "--file", str(source), "--validation-checks", "none"])
    assert from_file.exit_code == 0
    call = FakeClient.instances[-1].calls[-1]
    assert call[1] == "package Demo {}"
    assert call[3] == str(source.resolve())
    assert call[5]["validation_checks"] == "none"

    from_file_with_uri = invoke(
        ["validate", "text", "--file", str(source), "--uri", "memory:///demo.sysml"]
    )
    assert from_file_with_uri.exit_code == 0
    call = FakeClient.instances[-1].calls[-1]
    assert call[2] == "memory:///demo.sysml"
    assert call[3] is None

    bad_usage = invoke(["validate", "text"])
    assert bad_usage.exit_code == 2

    FakeClient.validate_result = validate_body(ok=False)
    failed = invoke(["validate", "text", "broken"])
    assert failed.exit_code == 1
    assert "bad syntax" in failed.output


def test_validate_text_file_read_errors(tmp_path, monkeypatch):
    bad = tmp_path / "bad.sysml"
    bad.write_bytes(b"\xff")
    decode_error = invoke(["validate", "text", "--file", str(bad)])
    assert decode_error.exit_code == 3
    assert "Cannot decode" in decode_error.output

    lookup_error = invoke(
        [
            "validate",
            "text",
            "--file",
            str(bad),
            "--encoding-errors",
            "does-not-exist",
        ]
    )
    assert lookup_error.exit_code == 3
    assert "unknown encoding option" in lookup_error.output
    assert "Traceback" not in lookup_error.output

    source = tmp_path / "source.sysml"
    source.write_text("package Demo {}", encoding="utf-8")

    def broken_read_text(self, encoding=None, errors=None):
        raise OSError("read failed")

    monkeypatch.setattr(cli_module.Path, "read_text", broken_read_text)
    read_error = invoke(["validate", "text", "--file", str(source)])
    assert read_error.exit_code == 3
    assert "Cannot read" in read_error.output


def test_validate_files_and_directory_options(tmp_path):
    first = tmp_path / "a.sysml"
    second = tmp_path / "b.sysml"
    first.write_text("package A {}", encoding="utf-8")
    second.write_text("package B {}", encoding="utf-8")

    files = invoke(
        [
            "validate",
            "files",
            str(first),
            str(second),
            "--uri-scheme",
            "file",
            "--language",
            "sysml",
            "--no-client-limits",
            "--limits",
            "none",
        ]
    )
    assert files.exit_code == 0
    client = FakeClient.instances[-1]
    assert client.enforce_client_limits is False
    assert client.limits is None
    assert client.calls[-1][0] == "validate_files"
    assert client.calls[-1][1][0].path == str(first.resolve())
    assert client.calls[-1][2]["validation_checks"] == "all"

    memory_files = invoke(["validate", "files", str(first), str(second), "--absolute-uris"])
    assert memory_files.exit_code == 0
    memory_call = FakeClient.instances[-1].calls[-1]
    assert memory_call[1][0].uri.startswith("memory:///")
    assert memory_call[1][0].path is None

    relative_memory_files = invoke(["validate", "files", str(first), str(second)])
    assert relative_memory_files.exit_code == 0
    relative_memory_call = FakeClient.instances[-1].calls[-1]
    assert relative_memory_call[1][0].uri == "memory:///a.sysml"

    no_files = invoke(["validate", "files"])
    assert no_files.exit_code == 2

    directory = invoke(
        [
            "validate",
            "directory",
            str(tmp_path),
            "--include",
            "**/*.sysml",
            "--exclude",
            "vendor/**",
            "--uri-scheme",
            "memory",
            "--absolute-uris",
            "--follow-symlinks",
        ]
    )
    assert directory.exit_code == 0
    _, options = FakeClient.directory_calls[-1]
    assert options["include"] == ("**/*.sysml",)
    assert options["exclude"] == ("vendor/**",)
    assert options["relative_uris"] is False
    assert options["follow_symlinks"] is True


def test_validate_files_local_errors_exit_three(tmp_path, monkeypatch):
    source = tmp_path / "a.sysml"
    source.write_text("package A {}", encoding="utf-8")

    def broken_commonpath(paths):
        raise ValueError("mixed roots")

    with monkeypatch.context() as patch:
        patch.setattr(cli_module.os.path, "commonpath", broken_commonpath)
        commonpath_error = invoke(["validate", "files", str(source)])
    assert commonpath_error.exit_code == 3
    assert "Cannot determine common root" in commonpath_error.output
    assert "Traceback" not in commonpath_error.output

    def broken_memory_uri(root, rel_posix, relative_uris):
        raise SysMLDirectoryError("bad generated URI")

    with monkeypatch.context() as patch:
        patch.setattr(cli_module, "_shared_memory_uri", broken_memory_uri)
        uri_error = invoke(["validate", "files", str(source)])
    assert uri_error.exit_code == 3
    assert "bad generated URI" in uri_error.output
    assert "Traceback" not in uri_error.output


def test_client_errors_exit_three(monkeypatch):
    class BrokenClient(FakeClient):
        def health(self):
            raise SysMLConnectionError("offline")

    monkeypatch.setattr(cli_module, "SysMLV2LSClient", BrokenClient)
    result = invoke(["health"])
    assert result.exit_code == 3
    assert "offline" in result.output


def test_client_value_errors_exit_three(monkeypatch):
    class BrokenClient(FakeClient):
        def __init__(self, *args, **kwargs):
            raise ValueError("bad client configuration")

    monkeypatch.setattr(cli_module, "SysMLV2LSClient", BrokenClient)
    result = invoke(["health"])
    assert result.exit_code == 3
    assert "bad client configuration" in result.output
    assert "Traceback" not in result.output
