import json

import pytest
import requests

from sysmlv2slclient import (
    HttpLimits,
    ServiceLimits,
    SysMLConnectionError,
    SysMLFile,
    SysMLResponseError,
    SysMLServiceError,
    SysMLV2LSClient,
    SysMLValidationLimitError,
    ValidateLimits,
)


def capabilities_body(limit_value=1000):
    return {
        "languages": [{"id": "sysml", "extensions": [".sysml"]}],
        "validationChecks": ["all", "none"],
        "standardLibrary": ["none"],
        "limits": {
            "validate": {
                "maxFiles": limit_value,
                "maxFileTextBytes": limit_value,
                "maxTotalTextBytes": limit_value,
                "validationTimeoutMs": limit_value,
            },
            "http": {"bodyLimitBytes": limit_value},
        },
    }


def validate_body(ok=True):
    return {
        "ok": ok,
        "diagnostics": [],
        "files": [
            {
                "uri": "memory:///demo.sysml",
                "language": "sysml",
                "parserErrors": 0,
                "lexerErrors": 0,
                "diagnostics": 0,
            }
        ],
        "meta": {
            "standardLibrary": "none",
            "validationChecks": "all",
            "elapsedMs": 1,
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


class FakeResponse(object):
    def __init__(self, payload, status_code=200, reason="OK"):
        self.payload = payload
        self.status_code = status_code
        self.reason = reason

    @property
    def text(self):
        if isinstance(self.payload, bytes):
            return self.payload.decode("utf-8", "replace")
        if isinstance(self.payload, str):
            return self.payload
        return json.dumps(self.payload)

    def json(self):
        if isinstance(self.payload, (bytes, str)):
            return json.loads(self.text)
        return self.payload


class FakeSession(object):
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append({"method": method, "url": url, "kwargs": kwargs})
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        if isinstance(response, tuple):
            return FakeResponse(response[0], status_code=response[1], reason=response[2])
        return FakeResponse(response)


def explicit_limits(limit_value=1000):
    return ServiceLimits(
        validate=ValidateLimits(limit_value, limit_value, limit_value, limit_value),
        http=HttpLimits(limit_value),
    )


def test_get_methods_and_headers():
    session = FakeSession(
        [
            {"ok": True, "service": "svc", "version": "1"},
            capabilities_body(),
            version_body(),
        ]
    )
    client = SysMLV2LSClient("http://example.test/", user_agent="UA", session=session)

    assert client.health().service == "svc"
    assert client.capabilities().limits.validate.max_files == 1000
    assert client.version().service.revision == "abc"
    assert [request["method"] for request in session.requests] == ["GET", "GET", "GET"]
    assert session.requests[0]["url"] == "http://example.test/healthz"
    assert session.requests[0]["kwargs"]["headers"]["User-Agent"] == "UA"
    assert session.requests[0]["kwargs"]["headers"]["Accept"] == "application/json"
    assert [request["kwargs"]["timeout"] for request in session.requests] == [30.0, 30.0, 30.0]


def test_validate_auto_fetches_and_caches_limits():
    session = FakeSession([capabilities_body(1000), validate_body(), validate_body()])
    client = SysMLV2LSClient("http://example.test", session=session)

    assert client.validate_text("package Demo {}", uri="memory:///demo.sysml").ok is True
    assert (
        client.validate_files([SysMLFile("package Demo {}", uri="memory:///demo.sysml")]).ok
        is True
    )
    assert [request["method"] for request in session.requests] == ["GET", "POST", "POST"]
    posted = session.requests[1]["kwargs"]["json"]
    assert posted["files"][0]["uri"] == "memory:///demo.sysml"
    assert session.requests[1]["kwargs"]["headers"]["Content-Type"] == "application/json"


def test_capabilities_refreshes_auto_cache():
    session = FakeSession([capabilities_body(1000), validate_body()])
    client = SysMLV2LSClient("http://example.test", session=session)
    client.capabilities()
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True
    assert [request["method"] for request in session.requests] == ["GET", "POST"]


def test_explicit_limits_and_dict_limits_do_not_fetch_capabilities():
    session = FakeSession([validate_body(), validate_body()])
    client = SysMLV2LSClient("http://example.test", session=session, limits=explicit_limits())
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True

    dict_client = SysMLV2LSClient(
        "http://example.test",
        session=session,
        limits=capabilities_body()["limits"],
    )
    assert dict_client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True
    assert [request["method"] for request in session.requests] == ["POST", "POST"]


def test_explicit_limits_survive_manual_capabilities_refresh():
    session = FakeSession([capabilities_body(1), validate_body()])
    client = SysMLV2LSClient("http://example.test", session=session, limits=explicit_limits(1000))
    assert client.capabilities().limits.validate.max_files == 1
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True


def test_none_limits_and_disabled_enforcement_skip_preflight():
    huge = "x" * 10
    session = FakeSession([validate_body(), validate_body()])
    no_known_limits = SysMLV2LSClient("http://example.test", session=session, limits=None)
    assert no_known_limits.validate([{"text": huge, "uri": "memory:///demo.sysml"}]).ok

    disabled = SysMLV2LSClient(
        "http://example.test",
        session=session,
        enforce_client_limits=False,
    )
    assert disabled.validate([{"text": huge, "uri": "memory:///demo.sysml"}]).ok
    assert [request["method"] for request in session.requests] == ["POST", "POST"]


def test_preflight_limit_failures():
    limits = ServiceLimits(ValidateLimits(1, 3, 5, 1), HttpLimits(500))
    client = SysMLV2LSClient("http://example.test", session=FakeSession([]), limits=limits)
    with pytest.raises(SysMLValidationLimitError):
        client.validate([{"text": "a"}, {"text": "b"}])
    with pytest.raises(SysMLValidationLimitError):
        client.validate([{"text": "abcd"}])

    total_limited = SysMLV2LSClient(
        "http://example.test",
        session=FakeSession([]),
        limits=ServiceLimits(ValidateLimits(10, 100, 5, 1), HttpLimits(500)),
    )
    with pytest.raises(SysMLValidationLimitError):
        total_limited.validate([{"text": "abc"}, {"text": "abc"}])

    tiny_body = SysMLV2LSClient(
        "http://example.test",
        session=FakeSession([]),
        limits=ServiceLimits(ValidateLimits(10, 100, 100, 1), HttpLimits(10)),
    )
    with pytest.raises(SysMLValidationLimitError):
        tiny_body.validate([{"text": "abc"}])


def test_option_validation_and_file_validation():
    client = SysMLV2LSClient("http://example.test", session=FakeSession([]), limits=None)
    with pytest.raises(ValueError):
        client.validate([], standard_library="standard")
    with pytest.raises(ValueError):
        client.validate([], validation_checks="sometimes")
    with pytest.raises(ValueError):
        client.validate([])
    with pytest.raises(ValueError):
        client.validate_text("x", uri="u", path="p")
    with pytest.raises(ValueError):
        client.validate_text("x", language="bad")


def test_validate_accepts_iterable_file_inputs():
    session = FakeSession([validate_body()])
    client = SysMLV2LSClient("http://example.test", session=session, limits=None)

    def file_inputs():
        yield {"text": "package Demo {}", "uri": "memory:///demo.sysml"}

    assert client.validate(file_inputs()).ok is True
    posted = session.requests[0]["kwargs"]["json"]
    assert posted["files"] == [{"text": "package Demo {}", "uri": "memory:///demo.sysml"}]


def test_http_errors_and_response_errors():
    client = SysMLV2LSClient(
        "http://example.test",
        session=FakeSession(
            [({"error": "bad_request", "message": "bad", "issues": [1]}, 400, "Bad Request")]
        ),
        limits=None,
    )
    with pytest.raises(SysMLServiceError) as captured:
        client.health()
    assert captured.value.error == "bad_request"
    assert captured.value.issues == [1]

    text_client = SysMLV2LSClient(
        "http://example.test",
        session=FakeSession([("not-json", 500, "Server Error")]),
        limits=None,
    )
    with pytest.raises(SysMLServiceError) as text_error:
        text_client.health()
    assert text_error.value.raw == "not-json"

    bad_json = SysMLV2LSClient(
        "http://example.test", session=FakeSession(["not-json"]), limits=None
    )
    with pytest.raises(SysMLResponseError):
        bad_json.health()

    bad_shape = SysMLV2LSClient("http://example.test", session=FakeSession([{}]), limits=None)
    with pytest.raises(SysMLResponseError):
        bad_shape.health()


def test_connection_errors_and_capability_fetch_failures_do_not_cache_empty_limits():
    session = FakeSession(
        [
            requests.exceptions.ConnectionError("no route"),
            requests.exceptions.Timeout("slow"),
        ]
    )
    client = SysMLV2LSClient("http://example.test", session=session)
    with pytest.raises(SysMLConnectionError):
        client.validate([{"text": "abc"}])
    with pytest.raises(SysMLConnectionError):
        client.validate([{"text": "abc"}])
    assert [request["method"] for request in session.requests] == ["GET", "GET"]


def test_base_url_validation_and_path_prefix():
    with pytest.raises(ValueError):
        SysMLV2LSClient("example.test")
    with pytest.raises(ValueError):
        SysMLV2LSClient("http://example.test?x=1")
    with pytest.raises(ValueError):
        SysMLV2LSClient("http://example.test#frag")
    session = FakeSession([{"ok": True, "service": "svc", "version": "1"}])
    client = SysMLV2LSClient("http://example.test/api", session=session, limits=None)
    client.health()
    assert session.requests[0]["url"] == "http://example.test/api/healthz"
