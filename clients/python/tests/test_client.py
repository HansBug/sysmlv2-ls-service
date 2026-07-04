import io
import json
import socket
import urllib.error

import pytest

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
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode("utf-8")


class FakeOpener(object):
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
        self.timeouts = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        self.timeouts.append(timeout)
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return FakeResponse(response)


def explicit_limits(limit_value=1000):
    return ServiceLimits(
        validate=ValidateLimits(limit_value, limit_value, limit_value, limit_value),
        http=HttpLimits(limit_value),
    )


def test_get_methods_and_headers():
    opener = FakeOpener([
        {"ok": True, "service": "svc", "version": "1"},
        capabilities_body(),
        version_body(),
    ])
    client = SysMLV2LSClient("http://example.test/", user_agent="UA", opener=opener)

    assert client.health().service == "svc"
    assert client.capabilities().limits.validate.max_files == 1000
    assert client.version().service.revision == "abc"
    assert [request.get_method() for request in opener.requests] == ["GET", "GET", "GET"]
    assert opener.requests[0].full_url == "http://example.test/healthz"
    assert opener.requests[0].get_header("User-agent") == "UA"
    assert opener.requests[0].get_header("Accept") == "application/json"
    assert opener.timeouts == [30.0, 30.0, 30.0]


def test_validate_auto_fetches_and_caches_limits():
    opener = FakeOpener([capabilities_body(1000), validate_body(), validate_body()])
    client = SysMLV2LSClient("http://example.test", opener=opener)

    assert client.validate_text("package Demo {}", uri="memory:///demo.sysml").ok is True
    assert client.validate_files([SysMLFile("package Demo {}", uri="memory:///demo.sysml")]).ok is True
    assert [request.get_method() for request in opener.requests] == ["GET", "POST", "POST"]
    posted = json.loads(opener.requests[1].data.decode("utf-8"))
    assert posted["files"][0]["uri"] == "memory:///demo.sysml"
    assert opener.requests[1].get_header("Content-type") == "application/json"


def test_capabilities_refreshes_auto_cache():
    opener = FakeOpener([capabilities_body(1000), validate_body()])
    client = SysMLV2LSClient("http://example.test", opener=opener)
    client.capabilities()
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True
    assert [request.get_method() for request in opener.requests] == ["GET", "POST"]


def test_explicit_limits_and_dict_limits_do_not_fetch_capabilities():
    opener = FakeOpener([validate_body(), validate_body()])
    client = SysMLV2LSClient("http://example.test", opener=opener, limits=explicit_limits())
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True

    dict_client = SysMLV2LSClient(
        "http://example.test",
        opener=opener,
        limits=capabilities_body()["limits"],
    )
    assert dict_client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True
    assert [request.get_method() for request in opener.requests] == ["POST", "POST"]


def test_explicit_limits_survive_manual_capabilities_refresh():
    opener = FakeOpener([capabilities_body(1), validate_body()])
    client = SysMLV2LSClient("http://example.test", opener=opener, limits=explicit_limits(1000))
    assert client.capabilities().limits.validate.max_files == 1
    assert client.validate([{"text": "abc", "uri": "memory:///demo.sysml"}]).ok is True


def test_none_limits_and_disabled_enforcement_skip_preflight():
    huge = "x" * 10
    opener = FakeOpener([validate_body(), validate_body()])
    no_known_limits = SysMLV2LSClient("http://example.test", opener=opener, limits=None)
    assert no_known_limits.validate([{"text": huge, "uri": "memory:///demo.sysml"}]).ok

    disabled = SysMLV2LSClient(
        "http://example.test",
        opener=opener,
        enforce_client_limits=False,
    )
    assert disabled.validate([{"text": huge, "uri": "memory:///demo.sysml"}]).ok
    assert [request.get_method() for request in opener.requests] == ["POST", "POST"]


def test_preflight_limit_failures():
    limits = ServiceLimits(ValidateLimits(1, 3, 5, 1), HttpLimits(500))
    client = SysMLV2LSClient("http://example.test", opener=FakeOpener([]), limits=limits)
    with pytest.raises(SysMLValidationLimitError):
        client.validate([{"text": "a"}, {"text": "b"}])
    with pytest.raises(SysMLValidationLimitError):
        client.validate([{"text": "abcd"}])

    total_limited = SysMLV2LSClient(
        "http://example.test",
        opener=FakeOpener([]),
        limits=ServiceLimits(ValidateLimits(10, 100, 5, 1), HttpLimits(500)),
    )
    with pytest.raises(SysMLValidationLimitError):
        total_limited.validate([{"text": "abc"}, {"text": "abc"}])

    tiny_body = SysMLV2LSClient(
        "http://example.test",
        opener=FakeOpener([]),
        limits=ServiceLimits(ValidateLimits(10, 100, 100, 1), HttpLimits(10)),
    )
    with pytest.raises(SysMLValidationLimitError):
        tiny_body.validate([{"text": "abc"}])


def test_option_validation_and_file_validation():
    client = SysMLV2LSClient("http://example.test", opener=FakeOpener([]), limits=None)
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


def test_http_errors_and_response_errors():
    http_json = urllib.error.HTTPError(
        "http://example.test",
        400,
        "Bad Request",
        {},
        io.BytesIO(b'{"error":"bad_request","message":"bad","issues":[1]}'),
    )
    client = SysMLV2LSClient("http://example.test", opener=FakeOpener([http_json]), limits=None)
    with pytest.raises(SysMLServiceError) as captured:
        client.health()
    assert captured.value.error == "bad_request"
    assert captured.value.issues == [1]

    http_text = urllib.error.HTTPError(
        "http://example.test",
        500,
        "Server Error",
        {},
        io.BytesIO(b"not-json"),
    )
    text_client = SysMLV2LSClient("http://example.test", opener=FakeOpener([http_text]), limits=None)
    with pytest.raises(SysMLServiceError) as text_error:
        text_client.health()
    assert text_error.value.raw == "not-json"

    bad_json = SysMLV2LSClient("http://example.test", opener=FakeOpener([b"not-json"]), limits=None)
    with pytest.raises(SysMLResponseError):
        bad_json.health()

    bad_shape = SysMLV2LSClient("http://example.test", opener=FakeOpener([{}]), limits=None)
    with pytest.raises(SysMLResponseError):
        bad_shape.health()


def test_connection_errors_and_capability_fetch_failures_do_not_cache_empty_limits():
    opener = FakeOpener([urllib.error.URLError("no route"), socket.timeout("slow")])
    client = SysMLV2LSClient("http://example.test", opener=opener)
    with pytest.raises(SysMLConnectionError):
        client.validate([{"text": "abc"}])
    with pytest.raises(SysMLConnectionError):
        client.validate([{"text": "abc"}])
    assert [request.get_method() for request in opener.requests] == ["GET", "GET"]


def test_base_url_validation_and_path_prefix():
    with pytest.raises(ValueError):
        SysMLV2LSClient("example.test")
    with pytest.raises(ValueError):
        SysMLV2LSClient("http://example.test?x=1")
    with pytest.raises(ValueError):
        SysMLV2LSClient("http://example.test#frag")
    opener = FakeOpener([{"ok": True, "service": "svc", "version": "1"}])
    client = SysMLV2LSClient("http://example.test/api", opener=opener, limits=None)
    client.health()
    assert opener.requests[0].full_url == "http://example.test/api/healthz"
