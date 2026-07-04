from sysmlv2slclient import (
    SysMLClientError,
    SysMLConnectionError,
    SysMLDirectoryError,
    SysMLResponseError,
    SysMLServiceError,
    SysMLValidationLimitError,
)


def test_error_classes_are_exported_and_readable():
    service_error = SysMLServiceError(
        400,
        "bad_request",
        "bad input",
        issues=[{"path": ["files"]}],
        raw={"error": "bad_request"},
    )
    assert str(service_error) == "400 bad_request: bad input"
    assert service_error.status_code == 400
    assert service_error.issues == [{"path": ["files"]}]
    assert isinstance(SysMLConnectionError("x"), SysMLClientError)
    assert isinstance(SysMLResponseError("x"), SysMLClientError)
    assert isinstance(SysMLValidationLimitError("x"), SysMLClientError)
    assert isinstance(SysMLDirectoryError("x"), SysMLClientError)
