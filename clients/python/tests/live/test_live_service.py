import os
from pathlib import Path

import pytest

from sysmlv2slclient import SysMLFile, SysMLServiceError, SysMLV2LSClient


def client():
    url = os.environ.get("SYSMLV2_LS_TEST_URL")
    if not url:
        pytest.skip("SYSMLV2_LS_TEST_URL is not set")
    return SysMLV2LSClient(url)


def test_health_and_revision():
    sdk = client()
    assert sdk.health().ok is True
    expected_revision = os.environ.get("SYSMLV2_LS_EXPECTED_REVISION")
    if not expected_revision:
        pytest.skip("SYSMLV2_LS_EXPECTED_REVISION is not set")
    assert sdk.version().service.revision == expected_revision


def test_capabilities_limits_match_expected_mode():
    sdk = client()
    expected = os.environ.get("SYSMLV2_LS_EXPECTED_LIMITS")
    if not expected:
        pytest.skip("SYSMLV2_LS_EXPECTED_LIMITS is not set")
    limits = sdk.capabilities().limits
    values = [
        limits.validate.max_files,
        limits.validate.max_file_text_bytes,
        limits.validate.max_total_text_bytes,
        limits.validate.validation_timeout_ms,
        limits.http.body_limit_bytes,
    ]
    if expected == "disabled":
        assert values == [None, None, None, None, None]
    elif expected == "default":
        assert values == [64, 524288, 1048576, 30000, 5242880]
    else:
        raise AssertionError("unknown SYSMLV2_LS_EXPECTED_LIMITS: %s" % expected)


def test_validate_text_and_files_and_directory(tmp_path):
    sdk = client()
    assert sdk.validate_text("package Demo { part def Vehicle; }").ok is True
    broken = sdk.validate_text("package Demo { part def }", validation_checks="none")
    assert broken.ok is False
    assert broken.files[0].parser_errors > 0

    multi = sdk.validate_files(
        [
            SysMLFile(uri="memory:///lib.sysml", text="package Lib { part def Base; }"),
            SysMLFile(
                uri="memory:///use.sysml",
                text="package Use { public import Lib::*; part base : Base; }",
            ),
        ]
    )
    assert multi.ok is True

    model = Path(tmp_path) / "model.sysml"
    model.write_text("package Dir { part def Vehicle; }", encoding="utf-8")
    assert sdk.validate_directory(tmp_path).ok is True


def test_service_errors_are_mapped():
    sdk = client()
    with pytest.raises(SysMLServiceError):
        sdk.validate_files(
            [
                SysMLFile(uri="memory:///same.sysml", text="package A {}"),
                SysMLFile(uri="memory:///same.sysml", text="package B {}"),
            ],
            validation_checks="none",
        )
