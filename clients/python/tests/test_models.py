import pytest

from sysmlv2slclient import (
    BuildInfo,
    CapabilitiesResponse,
    Diagnostic,
    FileValidationSummary,
    HealthResponse,
    HttpLimits,
    LanguageInfo,
    ServiceLimits,
    ServiceVersionInfo,
    SourcePosition,
    SourceRange,
    SysMLDiagnosticsError,
    SysMLFile,
    SysMLResponseError,
    UpstreamInfo,
    UpstreamSysML2LSInfo,
    ValidateLimits,
    ValidateMeta,
    ValidateResult,
    VersionResponse,
    __service_api_version__,
    __version__,
)


def diagnostic_dict(severity="error", code="E1"):
    data = {
        "severity": severity,
        "source": "sysml",
        "message": "bad",
        "uri": "memory:///bad.sysml",
        "range": {
            "start": {"line": 1, "character": 2},
            "end": {"line": 3, "character": 4},
        },
    }
    if code is not None:
        data["code"] = code
    return data


def validate_dict():
    return {
        "ok": False,
        "diagnostics": [
            diagnostic_dict("error", "E1"),
            diagnostic_dict("warning", None),
        ],
        "files": [
            {
                "uri": "memory:///bad.sysml",
                "language": "sysml",
                "parserErrors": 1,
                "lexerErrors": 0,
                "diagnostics": 2,
            }
        ],
        "meta": {
            "standardLibrary": "none",
            "validationChecks": "all",
            "elapsedMs": 1.5,
        },
    }


def capabilities_dict(disabled=False):
    value = None if disabled else 1
    return {
        "languages": [{"id": "sysml", "extensions": [".sysml"]}],
        "validationChecks": ["all", "none"],
        "standardLibrary": ["none"],
        "limits": {
            "validate": {
                "maxFiles": value,
                "maxFileTextBytes": value,
                "maxTotalTextBytes": value,
                "validationTimeoutMs": value,
            },
            "http": {"bodyLimitBytes": value},
        },
    }


def version_dict():
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


def test_exports_versions_and_request_file():
    assert __version__ == "0.1.0"
    assert __service_api_version__ == "v1"
    assert SysMLFile("x", uri="u").to_dict() == {"text": "x", "uri": "u"}
    path_file = SysMLFile.from_dict({"text": "x", "path": "p", "language": "sysml"})
    assert path_file.to_dict() == {"text": "x", "path": "p", "language": "sysml"}
    with pytest.raises(ValueError):
        SysMLFile("x", uri="u", path="p")
    with pytest.raises(ValueError):
        SysMLFile("x", language="bad")
    with pytest.raises(SysMLResponseError):
        SysMLFile.from_dict({})


def test_basic_nested_models_roundtrip():
    position = SourcePosition.from_dict({"line": 1, "character": 2})
    assert position.to_dict() == {"line": 1, "character": 2}
    source_range = SourceRange.from_dict(
        {"start": {"line": 1, "character": 2}, "end": {"line": 3, "character": 4}}
    )
    assert source_range.to_dict()["end"]["line"] == 3
    diagnostic = Diagnostic.from_dict(diagnostic_dict())
    assert diagnostic.to_dict()["code"] == "E1"
    no_code = Diagnostic.from_dict(diagnostic_dict(code=None))
    assert "code" not in no_code.to_dict()


def test_validate_result_helpers_and_errors():
    result = ValidateResult.from_dict(validate_dict())
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
    assert list(result.diagnostics_by_file()) == ["memory:///bad.sysml"]
    with pytest.raises(SysMLDiagnosticsError) as captured:
        result.raise_for_diagnostics()
    assert captured.value.result is result
    assert result.to_dict()["files"][0]["parserErrors"] == 1

    ok_data = validate_dict()
    ok_data["ok"] = True
    ok_data["diagnostics"] = [diagnostic_dict("warning", None)]
    ok_result = ValidateResult.from_dict(ok_data)
    assert ok_result.raise_for_diagnostics() is None


def test_individual_response_models_roundtrip():
    assert HealthResponse.from_dict({"ok": True, "service": "svc", "version": "1"}).to_dict() == {
        "ok": True,
        "service": "svc",
        "version": "1",
    }
    assert LanguageInfo.from_dict({"id": "sysml", "extensions": [".sysml"]}).to_dict() == {
        "id": "sysml",
        "extensions": [".sysml"],
    }
    assert FileValidationSummary.from_dict(validate_dict()["files"][0]).to_dict()["lexerErrors"] == 0
    assert ValidateMeta.from_dict(validate_dict()["meta"]).to_dict()["elapsedMs"] == 1.5


def test_capabilities_limits_roundtrip_and_shape_errors():
    capabilities = CapabilitiesResponse.from_dict(capabilities_dict(disabled=True))
    assert capabilities.limits.validate.max_files is None
    assert capabilities.to_dict()["limits"]["http"]["bodyLimitBytes"] is None
    explicit = ServiceLimits(
        validate=ValidateLimits(1, 2, 3, 4),
        http=HttpLimits(5),
    )
    assert explicit.to_dict()["validate"]["maxTotalTextBytes"] == 3
    with pytest.raises(SysMLResponseError):
        CapabilitiesResponse.from_dict({"languages": [], "validationChecks": [], "standardLibrary": []})
    with pytest.raises(SysMLResponseError):
        CapabilitiesResponse.from_dict(
            {"languages": {}, "validationChecks": [], "standardLibrary": [], "limits": {}}
        )


def test_version_roundtrip():
    response = VersionResponse.from_dict(version_dict())
    assert response.service.source_repository == "repo"
    assert response.upstream.sysml2ls.package_name == "pkg"
    assert response.build.node_version == "v24.0.0"
    assert response.to_dict()["service"]["sourceRepository"] == "repo"
    service = ServiceVersionInfo.from_dict(version_dict()["service"])
    upstream = UpstreamInfo(UpstreamSysML2LSInfo.from_dict(version_dict()["upstream"]["sysml2ls"]))
    build = BuildInfo.from_dict(version_dict()["build"])
    assert service.to_dict()["revision"] == "abc"
    assert upstream.to_dict()["sysml2ls"]["packageName"] == "pkg"
    assert build.to_dict()["nodeVersion"] == "v24.0.0"


def test_required_field_type_errors():
    with pytest.raises(SysMLResponseError):
        SourcePosition.from_dict(None)
    with pytest.raises(SysMLResponseError):
        SourceRange.from_dict({"start": [], "end": {}})
    with pytest.raises(SysMLResponseError):
        ValidateResult.from_dict({"ok": True, "diagnostics": {}, "files": [], "meta": {}})
