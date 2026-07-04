import json
import socket
import urllib.error
import urllib.parse
import urllib.request

from ._version import __version__
from .directory import collect_directory_files
from .errors import (
    SysMLConnectionError,
    SysMLResponseError,
    SysMLServiceError,
    SysMLValidationLimitError,
)
from .models import (
    CapabilitiesResponse,
    HealthResponse,
    ServiceLimits,
    SysMLFile,
    ValidateResult,
    VersionResponse,
)


class SysMLV2LSClient(object):
    def __init__(
        self,
        base_url,
        timeout=30.0,
        user_agent=None,
        opener=None,
        enforce_client_limits=True,
        limits="auto",
    ):
        self.base_url = self._normalize_base_url(base_url)
        self.timeout = timeout
        self.user_agent = user_agent or "sysmlv2slclient/%s" % __version__
        self._opener = opener or urllib.request.build_opener()
        self.enforce_client_limits = enforce_client_limits
        self._limits_mode = "auto"
        self._explicit_limits = None
        self._cached_capabilities = None
        self._cached_limits = None
        if limits is None:
            self._limits_mode = "none"
        elif limits == "auto":
            self._limits_mode = "auto"
        else:
            self._limits_mode = "explicit"
            self._explicit_limits = self._coerce_limits(limits)

    def _normalize_base_url(self, base_url):
        parts = urllib.parse.urlsplit(base_url)
        if parts.query or parts.fragment:
            raise ValueError("base_url must not include query or fragment")
        if not parts.scheme or not parts.netloc:
            raise ValueError("base_url must include scheme and host")
        return base_url.rstrip("/")

    def _url(self, path):
        return self.base_url + path

    def _request_json(self, method, path, payload=None):
        body = None
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self._url(path), data=body, headers=headers, method=method)
        try:
            response = self._opener.open(request, timeout=self.timeout)
            response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            raise self._service_error(error)
        except (urllib.error.URLError, socket.timeout, OSError) as error:
            raise SysMLConnectionError(str(error))
        try:
            return json.loads(response_body)
        except ValueError:
            raise SysMLResponseError("Response body is not valid JSON.")

    def _service_error(self, error):
        body = error.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except ValueError:
            return SysMLServiceError(
                error.code,
                "http_error",
                body or error.reason,
                raw=body,
            )
        return SysMLServiceError(
            error.code,
            parsed.get("error", "http_error"),
            parsed.get("message", error.reason),
            issues=parsed.get("issues"),
            raw=parsed,
        )

    def _coerce_limits(self, limits):
        if isinstance(limits, ServiceLimits):
            return limits
        return ServiceLimits.from_dict(limits)

    def _effective_limits(self):
        if not self.enforce_client_limits:
            return None
        if self._limits_mode == "none":
            return None
        if self._limits_mode == "explicit":
            return self._explicit_limits
        if self._cached_limits is None:
            self.refresh_capabilities()
        return self._cached_limits

    def _coerce_file(self, file_input):
        if isinstance(file_input, SysMLFile):
            return file_input
        return SysMLFile.from_dict(file_input)

    def _check_options(self, standard_library, validation_checks):
        if standard_library != "none":
            raise ValueError("standard_library must be 'none'")
        if validation_checks not in ("all", "none"):
            raise ValueError("validation_checks must be 'all' or 'none'")

    def _preflight_limits(self, files, body_bytes, limits):
        if limits is None:
            return
        validate_limits = limits.validate
        if validate_limits.max_files is not None and len(files) > validate_limits.max_files:
            raise SysMLValidationLimitError("Too many files for service limits.")
        total = 0
        for file_item in files:
            size = len(file_item.text.encode("utf-8"))
            total += size
            if (
                validate_limits.max_file_text_bytes is not None
                and size > validate_limits.max_file_text_bytes
            ):
                raise SysMLValidationLimitError("File text exceeds service limits.")
        if validate_limits.max_total_text_bytes is not None and total > validate_limits.max_total_text_bytes:
            raise SysMLValidationLimitError("Total file text exceeds service limits.")
        if limits.http.body_limit_bytes is not None and body_bytes > limits.http.body_limit_bytes:
            raise SysMLValidationLimitError("JSON request body exceeds service limits.")

    def health(self):
        return HealthResponse.from_dict(self._request_json("GET", "/healthz"))

    def capabilities(self):
        result = CapabilitiesResponse.from_dict(self._request_json("GET", "/v1/capabilities"))
        self._cached_capabilities = result
        if self._limits_mode == "auto":
            self._cached_limits = result.limits
        return result

    def refresh_capabilities(self):
        return self.capabilities()

    def version(self):
        return VersionResponse.from_dict(self._request_json("GET", "/v1/version"))

    def validate(self, files, standard_library="none", validation_checks="all"):
        self._check_options(standard_library, validation_checks)
        coerced = [self._coerce_file(file_item) for file_item in files]
        if not coerced:
            raise ValueError("files must be non-empty")
        payload = {
            "files": [file_item.to_dict() for file_item in coerced],
            "standardLibrary": standard_library,
            "validationChecks": validation_checks,
        }
        body_bytes = len(json.dumps(payload).encode("utf-8"))
        self._preflight_limits(coerced, body_bytes, self._effective_limits())
        return ValidateResult.from_dict(self._request_json("POST", "/v1/validate", payload))

    def validate_files(self, files, standard_library="none", validation_checks="all"):
        return self.validate(files, standard_library, validation_checks)

    def validate_text(
        self,
        text,
        uri=None,
        path=None,
        language=None,
        standard_library="none",
        validation_checks="all",
    ):
        return self.validate(
            [SysMLFile(text=text, uri=uri, path=path, language=language)],
            standard_library,
            validation_checks,
        )

    def validate_directory(
        self,
        path,
        include=("**/*.sysml",),
        exclude=None,
        uri_scheme="memory",
        relative_uris=True,
        language=None,
        encoding="utf-8",
        encoding_errors="strict",
        follow_symlinks=False,
        standard_library="none",
        validation_checks="all",
    ):
        files = collect_directory_files(
            path,
            include=include,
            exclude=exclude,
            uri_scheme=uri_scheme,
            relative_uris=relative_uris,
            language=language,
            encoding=encoding,
            encoding_errors=encoding_errors,
            follow_symlinks=follow_symlinks,
        )
        return self.validate(files, standard_library, validation_checks)
