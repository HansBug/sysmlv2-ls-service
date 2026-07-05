"""
High-level class client for ``sysmlv2-ls-service``.

The module keeps Python callers on service-owned DTOs while hiding HTTP
transport details. It uses :mod:`requests` for JSON requests and maps transport,
service, and malformed-response failures into stable SDK exceptions.

The module contains:

* :class:`SysMLV2LSClient` - class-based client for all current public service
  endpoints.

Example::

    >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
    >>> result = client.validate_text("package Demo {}", uri="memory:///demo.sysml")
    >>> hasattr(result, "ok")
    True
"""

import json
import urllib.parse

import requests

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
    """
    Class-based client for the SysML v2 language-service HTTP API.

    The client normalizes the service root URL, sends JSON through
    :class:`requests.Session`, parses service-owned DTOs, and optionally runs
    client-side request limit preflight using ``/v1/capabilities``.

    :param base_url: Service root URL, including scheme and host.
    :type base_url: str
    :param timeout: HTTP timeout in seconds, defaults to ``30.0``.
    :type timeout: float, optional
    :param user_agent: User-Agent header value, defaults to the SDK version.
    :type user_agent: str, optional
    :param session: Existing :class:`requests.Session` compatible object.
    :type session: requests.Session, optional
    :param enforce_client_limits: Whether to run known service-limit preflight.
    :type enforce_client_limits: bool, optional
    :param limits: ``"auto"``, ``None``, :class:`ServiceLimits`, or equivalent
        dictionary used for client-side request preflight.
    :type limits: str | None | ServiceLimits | dict, optional
    :raises ValueError: If ``base_url`` includes no scheme/host or includes a
        query string or fragment.

    Example::

        >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
        >>> isinstance(client.base_url, str)
        True
    """

    def __init__(
        self,
        base_url,
        timeout=30.0,
        user_agent=None,
        session=None,
        enforce_client_limits=True,
        limits="auto",
    ):
        self.base_url = self._normalize_base_url(base_url)
        self.timeout = timeout
        self.user_agent = user_agent or "sysmlv2slclient/%s" % __version__
        self._session = session or requests.Session()
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
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        kwargs = {
            "headers": headers,
            "timeout": self.timeout,
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
            kwargs["json"] = payload
        try:
            response = self._session.request(method, self._url(path), **kwargs)
        except requests.exceptions.RequestException as error:
            raise SysMLConnectionError(str(error))
        if response.status_code >= 400:
            raise self._service_error(response)
        try:
            return response.json()
        except ValueError:
            raise SysMLResponseError("Response body is not valid JSON.")

    def _service_error(self, response):
        body = response.text or ""
        try:
            parsed = response.json()
        except ValueError:
            return SysMLServiceError(
                response.status_code,
                "http_error",
                body or response.reason,
                raw=body,
            )
        return SysMLServiceError(
            response.status_code,
            parsed.get("error", "http_error"),
            parsed.get("message", response.reason),
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
        if (
            validate_limits.max_total_text_bytes is not None
            and total > validate_limits.max_total_text_bytes
        ):
            raise SysMLValidationLimitError("Total file text exceeds service limits.")
        if limits.http.body_limit_bytes is not None and body_bytes > limits.http.body_limit_bytes:
            raise SysMLValidationLimitError("JSON request body exceeds service limits.")

    def health(self):
        """
        Fetch service health metadata.

        :return: Parsed health response DTO.
        :rtype: HealthResponse
        :raises SysMLConnectionError: If the HTTP request cannot be completed.
        :raises SysMLServiceError: If the service returns an HTTP error.
        :raises SysMLResponseError: If the response body is not valid JSON or
            does not match the expected DTO shape.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.health)
            True
        """

        return HealthResponse.from_dict(self._request_json("GET", "/healthz"))

    def capabilities(self):
        """
        Fetch capabilities and refresh cached automatic limits.

        :return: Parsed service capabilities response DTO.
        :rtype: CapabilitiesResponse
        :raises SysMLConnectionError: If the HTTP request cannot be completed.
        :raises SysMLServiceError: If the service returns an HTTP error.
        :raises SysMLResponseError: If capabilities are malformed or missing
            required limits.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.capabilities)
            True
        """

        result = CapabilitiesResponse.from_dict(self._request_json("GET", "/v1/capabilities"))
        self._cached_capabilities = result
        if self._limits_mode == "auto":
            self._cached_limits = result.limits
        return result

    def refresh_capabilities(self):
        """
        Refresh cached capabilities and return them.

        :return: Parsed service capabilities response DTO.
        :rtype: CapabilitiesResponse
        :raises SysMLConnectionError: If the HTTP request cannot be completed.
        :raises SysMLServiceError: If the service returns an HTTP error.
        :raises SysMLResponseError: If capabilities are malformed.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> client.refresh_capabilities is client.capabilities
            False
        """

        return self.capabilities()

    def version(self):
        """
        Fetch service, upstream, and build version metadata.

        :return: Parsed version response DTO.
        :rtype: VersionResponse
        :raises SysMLConnectionError: If the HTTP request cannot be completed.
        :raises SysMLServiceError: If the service returns an HTTP error.
        :raises SysMLResponseError: If the response body is malformed.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.version)
            True
        """

        return VersionResponse.from_dict(self._request_json("GET", "/v1/version"))

    def validate(self, files, standard_library="none", validation_checks="all"):
        """
        Validate one request-local workspace.

        :param files: Iterable of :class:`SysMLFile` objects or equivalent
            dictionaries.
        :type files: iterable[SysMLFile | dict]
        :param standard_library: Service standard-library mode, currently
            ``"none"``.
        :type standard_library: str, optional
        :param validation_checks: ``"all"`` or ``"none"``.
        :type validation_checks: str, optional
        :return: Parsed validation result DTO.
        :rtype: ValidateResult
        :raises ValueError: If options are unsupported or ``files`` is empty.
        :raises SysMLValidationLimitError: If client-side limit preflight fails.
        :raises SysMLConnectionError: If the HTTP request cannot be completed.
        :raises SysMLServiceError: If the service returns an HTTP error.
        :raises SysMLResponseError: If the response body is malformed.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.validate)
            True
        """

        self._check_options(standard_library, validation_checks)
        coerced = []
        for file_item in files:
            coerced.append(self._coerce_file(file_item))
        if not coerced:
            raise ValueError("files must be non-empty")
        request_files = []
        for file_item in coerced:
            request_files.append(file_item.to_dict())
        payload = {
            "files": request_files,
            "standardLibrary": standard_library,
            "validationChecks": validation_checks,
        }
        body_bytes = len(json.dumps(payload).encode("utf-8"))
        self._preflight_limits(coerced, body_bytes, self._effective_limits())
        return ValidateResult.from_dict(self._request_json("POST", "/v1/validate", payload))

    def validate_files(self, files, standard_library="none", validation_checks="all"):
        """
        Validate explicit file DTOs or file dictionaries.

        :param files: Iterable of :class:`SysMLFile` objects or equivalent
            dictionaries.
        :type files: iterable[SysMLFile | dict]
        :param standard_library: Service standard-library mode, currently
            ``"none"``.
        :type standard_library: str, optional
        :param validation_checks: ``"all"`` or ``"none"``.
        :type validation_checks: str, optional
        :return: Parsed validation result DTO.
        :rtype: ValidateResult
        :raises ValueError: If options are unsupported or no files are supplied.
        :raises SysMLValidationLimitError: If client-side limit preflight fails.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.validate_files)
            True
        """

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
        """
        Validate a single in-memory text document.

        :param text: SysML or KerML document text.
        :type text: str
        :param uri: Optional document URI. Mutually exclusive with ``path``.
        :type uri: str, optional
        :param path: Optional document path. Mutually exclusive with ``uri``.
        :type path: str, optional
        :param language: Optional explicit language, ``"sysml"`` or
            ``"kerml"``.
        :type language: str, optional
        :param standard_library: Service standard-library mode.
        :type standard_library: str, optional
        :param validation_checks: ``"all"`` or ``"none"``.
        :type validation_checks: str, optional
        :return: Parsed validation result DTO.
        :rtype: ValidateResult
        :raises ValueError: If URI/path/language/options are invalid.
        :raises SysMLValidationLimitError: If client-side limit preflight fails.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.validate_text)
            True
        """

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
        """
        Validate files discovered under a directory root.

        :param path: Directory root whose matched files are submitted together.
        :type path: str | os.PathLike
        :param include: Relative glob pattern or patterns, defaults to
            ``("**/*.sysml",)``.
        :type include: tuple[str, ...] | callable, optional
        :param exclude: Relative glob pattern or patterns to skip.
        :type exclude: tuple[str, ...] | callable, optional
        :param uri_scheme: ``"memory"`` for generated memory URIs or
            ``"file"`` for absolute paths.
        :type uri_scheme: str, optional
        :param relative_uris: Whether memory URIs are relative to ``path``.
        :type relative_uris: bool, optional
        :param language: Optional explicit language for all collected files.
        :type language: str, optional
        :param encoding: File text encoding, defaults to ``"utf-8"``.
        :type encoding: str, optional
        :param encoding_errors: Decoding error handler.
        :type encoding_errors: str, optional
        :param follow_symlinks: Whether to follow symlinks that stay inside
            ``path``.
        :type follow_symlinks: bool, optional
        :param standard_library: Service standard-library mode.
        :type standard_library: str, optional
        :param validation_checks: ``"all"`` or ``"none"``.
        :type validation_checks: str, optional
        :return: Parsed validation result DTO.
        :rtype: ValidateResult
        :raises SysMLDirectoryError: If directory discovery, decoding, or
            root-boundary checks fail.
        :raises SysMLValidationLimitError: If client-side limit preflight fails.

        Example::

            >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
            >>> callable(client.validate_directory)
            True
        """

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
