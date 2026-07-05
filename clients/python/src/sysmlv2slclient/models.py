"""
Service-owned DTO models for the Python client.

The module parses JSON dictionaries returned by ``sysmlv2-ls-service`` into
typed dataclasses. It deliberately mirrors the public HTTP contract rather than
Langium or upstream ``sysml-2ls`` internals.

The module contains:

* :class:`SysMLFile` - request file input DTO.
* :class:`ValidateResult` - validation response DTO with diagnostic helpers.
* :class:`CapabilitiesResponse` - capabilities and effective limits DTO.
* :class:`VersionResponse` - service, upstream, and build metadata DTO.

Example::

    >>> file_item = SysMLFile("package Demo {}", uri="memory:///demo.sysml")
    >>> file_item.to_dict()["uri"]
    'memory:///demo.sysml'
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .errors import SysMLDiagnosticsError, SysMLResponseError


def _require(data, key):
    try:
        return data[key]
    except (KeyError, TypeError):
        raise SysMLResponseError("Response missing required field: %s" % key)


def _list(data, key):
    value = _require(data, key)
    if not isinstance(value, list):
        raise SysMLResponseError("Response field must be a list: %s" % key)
    return value


def _dict(data, key):
    value = _require(data, key)
    if not isinstance(value, dict):
        raise SysMLResponseError("Response field must be an object: %s" % key)
    return value


@dataclass
class SysMLFile:
    """
    Request-local SysML/KerML document input.

    :param text: Document text sent to the validation service.
    :type text: str
    :param uri: Optional document URI. Mutually exclusive with ``path``.
    :type uri: str, optional
    :param path: Optional document path. Mutually exclusive with ``uri``.
    :type path: str, optional
    :param language: Optional explicit language, ``"sysml"`` or ``"kerml"``.
    :type language: str, optional
    :raises ValueError: If both ``uri`` and ``path`` are set or language is
        unsupported.

    Example::

        >>> SysMLFile("package Demo {}", uri="memory:///demo.sysml").to_dict()["text"]
        'package Demo {}'
    """

    text: str
    uri: Optional[str] = None
    path: Optional[str] = None
    language: Optional[str] = None

    def __post_init__(self):
        if self.uri is not None and self.path is not None:
            raise ValueError("uri and path are mutually exclusive")
        if self.language is not None and self.language not in ("sysml", "kerml"):
            raise ValueError("language must be 'sysml' or 'kerml'")

    @classmethod
    def from_dict(cls, data):
        """
        Parse a request file DTO from a dictionary.

        :param data: Dictionary with ``text`` and optional identifier fields.
        :type data: dict
        :return: Parsed file DTO.
        :rtype: SysMLFile

        Example::

            >>> SysMLFile.from_dict({"text": "package Demo {}"}).text
            'package Demo {}'
        """

        return cls(
            text=_require(data, "text"),
            uri=data.get("uri"),
            path=data.get("path"),
            language=data.get("language"),
        )

    def to_dict(self):
        """
        Convert this file DTO to the service request shape.

        :return: JSON-serializable file dictionary.
        :rtype: dict

        Example::

            >>> SysMLFile("x", uri="memory:///x.sysml").to_dict()["uri"]
            'memory:///x.sysml'
        """

        data = {"text": self.text}
        if self.uri is not None:
            data["uri"] = self.uri
        if self.path is not None:
            data["path"] = self.path
        if self.language is not None:
            data["language"] = self.language
        return data


@dataclass
class SourcePosition:
    """
    Zero-based source position in a diagnostic range.

    :param line: Source line number.
    :type line: int
    :param character: Source character offset.
    :type character: int

    Example::

        >>> SourcePosition(1, 2).to_dict()
        {'line': 1, 'character': 2}
    """

    line: int
    character: int

    @classmethod
    def from_dict(cls, data):
        """
        Parse a source position from a dictionary.

        :param data: Dictionary with ``line`` and ``character``.
        :type data: dict
        :return: Parsed source position.
        :rtype: SourcePosition

        Example::

            >>> SourcePosition.from_dict({"line": 1, "character": 2}).line
            1
        """

        return cls(line=_require(data, "line"), character=_require(data, "character"))

    def to_dict(self):
        """
        Convert this position to the service DTO shape.

        :return: JSON-serializable source position dictionary.
        :rtype: dict

        Example::

            >>> SourcePosition(1, 2).to_dict()["character"]
            2
        """

        return {"line": self.line, "character": self.character}


@dataclass
class SourceRange:
    """
    Start and end positions for a diagnostic.

    :param start: Start position.
    :type start: SourcePosition
    :param end: End position.
    :type end: SourcePosition

    Example::

        >>> SourceRange(SourcePosition(1, 2), SourcePosition(1, 3)).to_dict()["end"]["character"]
        3
    """

    start: SourcePosition
    end: SourcePosition

    @classmethod
    def from_dict(cls, data):
        """
        Parse a source range from a dictionary.

        :param data: Dictionary with ``start`` and ``end`` positions.
        :type data: dict
        :return: Parsed source range.
        :rtype: SourceRange

        Example::

            >>> SourceRange.from_dict({"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 1}}).end.character
            1
        """

        return cls(
            start=SourcePosition.from_dict(_dict(data, "start")),
            end=SourcePosition.from_dict(_dict(data, "end")),
        )

    def to_dict(self):
        """
        Convert this range to the service DTO shape.

        :return: JSON-serializable range dictionary.
        :rtype: dict

        Example::

            >>> rng = SourceRange(SourcePosition(0, 0), SourcePosition(0, 1))
            >>> rng.to_dict()["start"]["line"]
            0
        """

        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Diagnostic:
    """
    Normalized service diagnostic.

    :param severity: Diagnostic severity name.
    :type severity: str
    :param source: Diagnostic source.
    :type source: str
    :param message: Human-readable diagnostic message.
    :type message: str
    :param uri: Document URI.
    :type uri: str
    :param range: Source range.
    :type range: SourceRange
    :param code: Optional diagnostic code.
    :type code: str | int, optional
    :param raw: Original diagnostic dictionary.
    :type raw: dict, optional

    Example::

        >>> rng = SourceRange(SourcePosition(0, 0), SourcePosition(0, 1))
        >>> Diagnostic("error", "sysml", "bad", "memory:///x.sysml", rng).severity
        'error'
    """

    severity: str
    source: str
    message: str
    uri: str
    range: SourceRange
    code: Optional[Union[str, int]] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse a normalized diagnostic from a dictionary.

        :param data: Service diagnostic dictionary.
        :type data: dict
        :return: Parsed diagnostic DTO.
        :rtype: Diagnostic

        Example::

            >>> data = {"severity": "error", "source": "sysml", "message": "bad", "uri": "memory:///x.sysml", "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 1}}}
            >>> Diagnostic.from_dict(data).severity
            'error'
        """

        return cls(
            severity=_require(data, "severity"),
            source=_require(data, "source"),
            message=_require(data, "message"),
            uri=_require(data, "uri"),
            range=SourceRange.from_dict(_dict(data, "range")),
            code=data.get("code"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert this diagnostic to the service DTO shape.

        :return: JSON-serializable diagnostic dictionary.
        :rtype: dict

        Example::

            >>> rng = SourceRange(SourcePosition(0, 0), SourcePosition(0, 1))
            >>> Diagnostic("error", "sysml", "bad", "memory:///x.sysml", rng).to_dict()["severity"]
            'error'
        """

        data = {
            "severity": self.severity,
            "source": self.source,
            "message": self.message,
            "uri": self.uri,
            "range": self.range.to_dict(),
        }
        if self.code is not None:
            data["code"] = self.code
        return data


@dataclass
class FileValidationSummary:
    """
    Per-file validation summary.

    :param uri: Canonical document URI.
    :type uri: str
    :param language: Resolved document language.
    :type language: str
    :param parser_errors: Number of parser errors.
    :type parser_errors: int
    :param lexer_errors: Number of lexer errors.
    :type lexer_errors: int
    :param diagnostics: Number of diagnostics for this file.
    :type diagnostics: int
    :param raw: Original file summary dictionary.
    :type raw: dict, optional

    Example::

        >>> FileValidationSummary("memory:///x.sysml", "sysml", 0, 0, 0).diagnostics
        0
    """

    uri: str
    language: str
    parser_errors: int
    lexer_errors: int
    diagnostics: int
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse a per-file validation summary.

        :param data: File summary dictionary.
        :type data: dict
        :return: Parsed file validation summary.
        :rtype: FileValidationSummary

        Example::

            >>> data = {"uri": "memory:///x.sysml", "language": "sysml", "parserErrors": 0, "lexerErrors": 0, "diagnostics": 0}
            >>> FileValidationSummary.from_dict(data).language
            'sysml'
        """

        return cls(
            uri=_require(data, "uri"),
            language=_require(data, "language"),
            parser_errors=_require(data, "parserErrors"),
            lexer_errors=_require(data, "lexerErrors"),
            diagnostics=_require(data, "diagnostics"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert this summary to the service DTO shape.

        :return: JSON-serializable file summary dictionary.
        :rtype: dict

        Example::

            >>> FileValidationSummary("memory:///x.sysml", "sysml", 0, 0, 0).to_dict()["diagnostics"]
            0
        """

        return {
            "uri": self.uri,
            "language": self.language,
            "parserErrors": self.parser_errors,
            "lexerErrors": self.lexer_errors,
            "diagnostics": self.diagnostics,
        }


@dataclass
class ValidateMeta:
    """
    Metadata for one validation response.

    :param standard_library: Service standard-library mode.
    :type standard_library: str
    :param validation_checks: Validation-check mode.
    :type validation_checks: str
    :param elapsed_ms: Service-side elapsed time in milliseconds.
    :type elapsed_ms: float
    :param raw: Original metadata dictionary.
    :type raw: dict, optional

    Example::

        >>> ValidateMeta("none", "all", 1.0).to_dict()["validationChecks"]
        'all'
    """

    standard_library: str
    validation_checks: str
    elapsed_ms: float
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse validation response metadata.

        :param data: Validation metadata dictionary.
        :type data: dict
        :return: Parsed metadata DTO.
        :rtype: ValidateMeta

        Example::

            >>> data = {"standardLibrary": "none", "validationChecks": "all", "elapsedMs": 1}
            >>> ValidateMeta.from_dict(data).validation_checks
            'all'
        """

        return cls(
            standard_library=_require(data, "standardLibrary"),
            validation_checks=_require(data, "validationChecks"),
            elapsed_ms=_require(data, "elapsedMs"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert this metadata to the service DTO shape.

        :return: JSON-serializable validation metadata dictionary.
        :rtype: dict

        Example::

            >>> ValidateMeta("none", "all", 1).to_dict()["standardLibrary"]
            'none'
        """

        return {
            "standardLibrary": self.standard_library,
            "validationChecks": self.validation_checks,
            "elapsedMs": self.elapsed_ms,
        }


@dataclass
class ValidateResult:
    """
    Validation result returned by ``POST /v1/validate``.

    :param ok: Whether validation succeeded without error diagnostics.
    :type ok: bool
    :param diagnostics: Normalized diagnostics.
    :type diagnostics: list[Diagnostic]
    :param files: Per-file summaries.
    :type files: list[FileValidationSummary]
    :param meta: Response metadata.
    :type meta: ValidateMeta
    :param raw: Original response dictionary.
    :type raw: dict

    Example::

        >>> meta = ValidateMeta("none", "all", 1)
        >>> ValidateResult(True, [], [], meta, {}).errors
        []
    """

    ok: bool
    diagnostics: List[Diagnostic]
    files: List[FileValidationSummary]
    meta: ValidateMeta
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        """
        Parse a validation result from a service response dictionary.

        :param data: Validate response dictionary.
        :type data: dict
        :return: Parsed validation result.
        :rtype: ValidateResult

        Example::

            >>> data = {"ok": True, "diagnostics": [], "files": [], "meta": {"standardLibrary": "none", "validationChecks": "all", "elapsedMs": 1}}
            >>> ValidateResult.from_dict(data).ok
            True
        """

        diagnostics = []
        for item in _list(data, "diagnostics"):
            diagnostics.append(Diagnostic.from_dict(item))
        files = []
        for item in _list(data, "files"):
            files.append(FileValidationSummary.from_dict(item))
        return cls(
            ok=_require(data, "ok"),
            diagnostics=diagnostics,
            files=files,
            meta=ValidateMeta.from_dict(_dict(data, "meta")),
            raw=dict(data),
        )

    @property
    def errors(self):
        """
        Return diagnostics whose severity is ``"error"``.

        :return: Error diagnostics.
        :rtype: list[Diagnostic]

        Example::

            >>> ValidateResult(True, [], [], ValidateMeta("none", "all", 1), {}).errors
            []
        """

        errors = []
        for item in self.diagnostics:
            if item.severity == "error":
                errors.append(item)
        return errors

    @property
    def warnings(self):
        """
        Return diagnostics whose severity is ``"warning"``.

        :return: Warning diagnostics.
        :rtype: list[Diagnostic]

        Example::

            >>> ValidateResult(True, [], [], ValidateMeta("none", "all", 1), {}).warnings
            []
        """

        warnings = []
        for item in self.diagnostics:
            if item.severity == "warning":
                warnings.append(item)
        return warnings

    def diagnostics_by_file(self):
        """
        Group diagnostics by document URI.

        :return: Mapping from document URI to diagnostics for that document.
        :rtype: dict[str, list[Diagnostic]]

        Example::

            >>> ValidateResult(True, [], [], ValidateMeta("none", "all", 1), {}).diagnostics_by_file()
            {}
        """

        grouped = {}
        for diagnostic in self.diagnostics:
            grouped.setdefault(diagnostic.uri, []).append(diagnostic)
        return grouped

    def raise_for_diagnostics(self):
        """
        Raise when validation result contains error diagnostics.

        :return: ``None`` when the result has no validation errors.
        :rtype: None
        :raises SysMLDiagnosticsError: If ``ok`` is false or error diagnostics
            are present.

        Example::

            >>> ValidateResult(True, [], [], ValidateMeta("none", "all", 1), {}).raise_for_diagnostics() is None
            True
        """

        if not self.ok or self.errors:
            raise SysMLDiagnosticsError(self)
        return None

    def to_dict(self):
        """
        Convert this validation result to the service DTO shape.

        :return: JSON-serializable validate response dictionary.
        :rtype: dict

        Example::

            >>> ValidateResult(True, [], [], ValidateMeta("none", "all", 1), {}).to_dict()["ok"]
            True
        """

        diagnostics = []
        for item in self.diagnostics:
            diagnostics.append(item.to_dict())
        files = []
        for item in self.files:
            files.append(item.to_dict())
        return {
            "ok": self.ok,
            "diagnostics": diagnostics,
            "files": files,
            "meta": self.meta.to_dict(),
        }


@dataclass
class HealthResponse:
    """
    Health response returned by ``GET /healthz``.

    :param ok: Service liveness status.
    :type ok: bool
    :param service: Service name.
    :type service: str
    :param version: Service version.
    :type version: str
    :param raw: Original response dictionary.
    :type raw: dict

    Example::

        >>> HealthResponse(True, "svc", "1", {}).to_dict()["ok"]
        True
    """

    ok: bool
    service: str
    version: str
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        """
        Parse a health response from a dictionary.

        :param data: Health response dictionary.
        :type data: dict
        :return: Parsed health response.
        :rtype: HealthResponse

        Example::

            >>> HealthResponse.from_dict({"ok": True, "service": "svc", "version": "1"}).service
            'svc'
        """

        return cls(
            ok=_require(data, "ok"),
            service=_require(data, "service"),
            version=_require(data, "version"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert this health response to the service DTO shape.

        :return: JSON-serializable health response dictionary.
        :rtype: dict

        Example::

            >>> HealthResponse(True, "svc", "1", {}).to_dict()["version"]
            '1'
        """

        return {"ok": self.ok, "service": self.service, "version": self.version}


@dataclass
class LanguageInfo:
    """
    Supported language metadata.

    :param id: Language identifier.
    :type id: str
    :param extensions: File extensions associated with the language.
    :type extensions: list[str]
    :param raw: Original language dictionary.
    :type raw: dict, optional

    Example::

        >>> LanguageInfo("sysml", [".sysml"]).extensions
        ['.sysml']
    """

    id: str
    extensions: List[str]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse supported language metadata.

        :param data: Language metadata dictionary.
        :type data: dict
        :return: Parsed language metadata.
        :rtype: LanguageInfo

        Example::

            >>> LanguageInfo.from_dict({"id": "sysml", "extensions": [".sysml"]}).id
            'sysml'
        """

        return cls(id=_require(data, "id"), extensions=_list(data, "extensions"), raw=dict(data))

    def to_dict(self):
        """
        Convert this language metadata to the service DTO shape.

        :return: JSON-serializable language metadata dictionary.
        :rtype: dict

        Example::

            >>> LanguageInfo("sysml", [".sysml"]).to_dict()["extensions"]
            ['.sysml']
        """

        return {"id": self.id, "extensions": list(self.extensions)}


@dataclass
class ValidateLimits:
    """
    Effective validation request limits.

    :param max_files: Maximum files per request, or ``None`` if disabled.
    :type max_files: int, optional
    :param max_file_text_bytes: Maximum UTF-8 bytes per file, or ``None``.
    :type max_file_text_bytes: int, optional
    :param max_total_text_bytes: Maximum total UTF-8 bytes, or ``None``.
    :type max_total_text_bytes: int, optional
    :param validation_timeout_ms: Validation timeout in milliseconds, or
        ``None`` if disabled.
    :type validation_timeout_ms: int, optional
    :param raw: Original limits dictionary.
    :type raw: dict, optional

    Example::

        >>> ValidateLimits(1, 2, 3, 4).to_dict()["maxFiles"]
        1
    """

    max_files: Optional[int]
    max_file_text_bytes: Optional[int]
    max_total_text_bytes: Optional[int]
    validation_timeout_ms: Optional[int]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse validation limits from a dictionary.

        :param data: Validation limits dictionary.
        :type data: dict
        :return: Parsed validation limits.
        :rtype: ValidateLimits

        Example::

            >>> data = {"maxFiles": 1, "maxFileTextBytes": 2, "maxTotalTextBytes": 3, "validationTimeoutMs": 4}
            >>> ValidateLimits.from_dict(data).max_files
            1
        """

        return cls(
            max_files=_require(data, "maxFiles"),
            max_file_text_bytes=_require(data, "maxFileTextBytes"),
            max_total_text_bytes=_require(data, "maxTotalTextBytes"),
            validation_timeout_ms=_require(data, "validationTimeoutMs"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert these validation limits to the service DTO shape.

        :return: JSON-serializable validation limits dictionary.
        :rtype: dict

        Example::

            >>> ValidateLimits(1, 2, 3, 4).to_dict()["validationTimeoutMs"]
            4
        """

        return {
            "maxFiles": self.max_files,
            "maxFileTextBytes": self.max_file_text_bytes,
            "maxTotalTextBytes": self.max_total_text_bytes,
            "validationTimeoutMs": self.validation_timeout_ms,
        }


@dataclass
class HttpLimits:
    """
    Effective HTTP request limits.

    :param body_limit_bytes: HTTP body limit in bytes, or ``None`` if disabled.
    :type body_limit_bytes: int, optional
    :param raw: Original HTTP limits dictionary.
    :type raw: dict, optional

    Example::

        >>> HttpLimits(None).to_dict()["bodyLimitBytes"] is None
        True
    """

    body_limit_bytes: Optional[int]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse HTTP limits from a dictionary.

        :param data: HTTP limits dictionary.
        :type data: dict
        :return: Parsed HTTP limits.
        :rtype: HttpLimits

        Example::

            >>> HttpLimits.from_dict({"bodyLimitBytes": None}).body_limit_bytes is None
            True
        """

        return cls(body_limit_bytes=_require(data, "bodyLimitBytes"), raw=dict(data))

    def to_dict(self):
        """
        Convert these HTTP limits to the service DTO shape.

        :return: JSON-serializable HTTP limits dictionary.
        :rtype: dict

        Example::

            >>> HttpLimits(5).to_dict()["bodyLimitBytes"]
            5
        """

        return {"bodyLimitBytes": self.body_limit_bytes}


@dataclass
class ServiceLimits:
    """
    Effective service-owned request limits.

    :param validate: Validation limits.
    :type validate: ValidateLimits
    :param http: HTTP request limits.
    :type http: HttpLimits
    :param raw: Original limits dictionary.
    :type raw: dict, optional

    Example::

        >>> limits = ServiceLimits(ValidateLimits(1, 2, 3, 4), HttpLimits(5))
        >>> limits.http.body_limit_bytes
        5
    """

    validate: ValidateLimits
    http: HttpLimits
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse complete service limits from a dictionary.

        :param data: Service limits dictionary.
        :type data: dict
        :return: Parsed service limits.
        :rtype: ServiceLimits

        Example::

            >>> data = {"validate": {"maxFiles": 1, "maxFileTextBytes": 2, "maxTotalTextBytes": 3, "validationTimeoutMs": 4}, "http": {"bodyLimitBytes": 5}}
            >>> ServiceLimits.from_dict(data).http.body_limit_bytes
            5
        """

        return cls(
            validate=ValidateLimits.from_dict(_dict(data, "validate")),
            http=HttpLimits.from_dict(_dict(data, "http")),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert service limits to the service DTO shape.

        :return: JSON-serializable service limits dictionary.
        :rtype: dict

        Example::

            >>> ServiceLimits(ValidateLimits(1, 2, 3, 4), HttpLimits(5)).to_dict()["http"]["bodyLimitBytes"]
            5
        """

        return {"validate": self.validate.to_dict(), "http": self.http.to_dict()}


@dataclass
class CapabilitiesResponse:
    """
    Capabilities response returned by ``GET /v1/capabilities``.

    :param languages: Supported languages.
    :type languages: list[LanguageInfo]
    :param validation_checks: Supported validation-check modes.
    :type validation_checks: list[str]
    :param standard_library: Supported standard-library modes.
    :type standard_library: list[str]
    :param limits: Effective service-owned limits.
    :type limits: ServiceLimits
    :param raw: Original response dictionary.
    :type raw: dict

    Example::

        >>> limits = ServiceLimits(ValidateLimits(1, 2, 3, 4), HttpLimits(5))
        >>> CapabilitiesResponse([], ["all"], ["none"], limits, {}).validation_checks
        ['all']
    """

    languages: List[LanguageInfo]
    validation_checks: List[str]
    standard_library: List[str]
    limits: ServiceLimits
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        """
        Parse capabilities from a service response dictionary.

        :param data: Capabilities response dictionary.
        :type data: dict
        :return: Parsed capabilities response.
        :rtype: CapabilitiesResponse

        Example::

            >>> data = {"languages": [], "validationChecks": ["all"], "standardLibrary": ["none"], "limits": {"validate": {"maxFiles": 1, "maxFileTextBytes": 2, "maxTotalTextBytes": 3, "validationTimeoutMs": 4}, "http": {"bodyLimitBytes": 5}}}
            >>> CapabilitiesResponse.from_dict(data).standard_library
            ['none']
        """

        languages = []
        for item in _list(data, "languages"):
            languages.append(LanguageInfo.from_dict(item))
        return cls(
            languages=languages,
            validation_checks=_list(data, "validationChecks"),
            standard_library=_list(data, "standardLibrary"),
            limits=ServiceLimits.from_dict(_dict(data, "limits")),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert capabilities to the service DTO shape.

        :return: JSON-serializable capabilities dictionary.
        :rtype: dict

        Example::

            >>> limits = ServiceLimits(ValidateLimits(1, 2, 3, 4), HttpLimits(5))
            >>> CapabilitiesResponse([], ["all"], ["none"], limits, {}).to_dict()["validationChecks"]
            ['all']
        """

        languages = []
        for item in self.languages:
            languages.append(item.to_dict())
        return {
            "languages": languages,
            "validationChecks": list(self.validation_checks),
            "standardLibrary": list(self.standard_library),
            "limits": self.limits.to_dict(),
        }


@dataclass
class ServiceVersionInfo:
    """
    Service version metadata.

    :param name: Service name.
    :type name: str
    :param version: Service version.
    :type version: str
    :param revision: Service source revision.
    :type revision: str
    :param source_repository: Source repository URL.
    :type source_repository: str
    :param raw: Original service version dictionary.
    :type raw: dict, optional

    Example::

        >>> ServiceVersionInfo("svc", "1", "abc", "repo").revision
        'abc'
    """

    name: str
    version: str
    revision: str
    source_repository: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse service version metadata from a dictionary.

        :param data: Service version dictionary.
        :type data: dict
        :return: Parsed service version metadata.
        :rtype: ServiceVersionInfo

        Example::

            >>> data = {"name": "svc", "version": "1", "revision": "abc", "sourceRepository": "repo"}
            >>> ServiceVersionInfo.from_dict(data).name
            'svc'
        """

        return cls(
            name=_require(data, "name"),
            version=_require(data, "version"),
            revision=_require(data, "revision"),
            source_repository=_require(data, "sourceRepository"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert service version metadata to the service DTO shape.

        :return: JSON-serializable service version dictionary.
        :rtype: dict

        Example::

            >>> ServiceVersionInfo("svc", "1", "abc", "repo").to_dict()["revision"]
            'abc'
        """

        return {
            "name": self.name,
            "version": self.version,
            "revision": self.revision,
            "sourceRepository": self.source_repository,
        }


@dataclass
class UpstreamSysML2LSInfo:
    """
    Upstream ``sysml-2ls`` package metadata.

    :param version: Upstream package version.
    :type version: str
    :param revision: Upstream submodule revision.
    :type revision: str
    :param package_name: Upstream package name.
    :type package_name: str
    :param repository: Upstream repository URL.
    :type repository: str
    :param raw: Original upstream dictionary.
    :type raw: dict, optional

    Example::

        >>> UpstreamSysML2LSInfo("1", "abc", "pkg", "repo").package_name
        'pkg'
    """

    version: str
    revision: str
    package_name: str
    repository: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse upstream ``sysml-2ls`` metadata from a dictionary.

        :param data: Upstream metadata dictionary.
        :type data: dict
        :return: Parsed upstream metadata.
        :rtype: UpstreamSysML2LSInfo

        Example::

            >>> data = {"version": "1", "revision": "abc", "packageName": "pkg", "repository": "repo"}
            >>> UpstreamSysML2LSInfo.from_dict(data).repository
            'repo'
        """

        return cls(
            version=_require(data, "version"),
            revision=_require(data, "revision"),
            package_name=_require(data, "packageName"),
            repository=_require(data, "repository"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert upstream metadata to the service DTO shape.

        :return: JSON-serializable upstream metadata dictionary.
        :rtype: dict

        Example::

            >>> UpstreamSysML2LSInfo("1", "abc", "pkg", "repo").to_dict()["packageName"]
            'pkg'
        """

        return {
            "version": self.version,
            "revision": self.revision,
            "packageName": self.package_name,
            "repository": self.repository,
        }


@dataclass
class UpstreamInfo:
    """
    Upstream dependency metadata group.

    :param sysml2ls: Upstream ``sysml-2ls`` metadata.
    :type sysml2ls: UpstreamSysML2LSInfo
    :param raw: Original upstream group dictionary.
    :type raw: dict, optional

    Example::

        >>> upstream = UpstreamInfo(UpstreamSysML2LSInfo("1", "abc", "pkg", "repo"))
        >>> upstream.sysml2ls.version
        '1'
    """

    sysml2ls: UpstreamSysML2LSInfo
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse upstream metadata group from a dictionary.

        :param data: Upstream metadata group dictionary.
        :type data: dict
        :return: Parsed upstream metadata group.
        :rtype: UpstreamInfo

        Example::

            >>> data = {"sysml2ls": {"version": "1", "revision": "abc", "packageName": "pkg", "repository": "repo"}}
            >>> UpstreamInfo.from_dict(data).sysml2ls.package_name
            'pkg'
        """

        return cls(
            sysml2ls=UpstreamSysML2LSInfo.from_dict(_dict(data, "sysml2ls")),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert upstream metadata group to the service DTO shape.

        :return: JSON-serializable upstream group dictionary.
        :rtype: dict

        Example::

            >>> upstream = UpstreamInfo(UpstreamSysML2LSInfo("1", "abc", "pkg", "repo"))
            >>> upstream.to_dict()["sysml2ls"]["version"]
            '1'
        """

        return {"sysml2ls": self.sysml2ls.to_dict()}


@dataclass
class BuildInfo:
    """
    Service build metadata.

    :param date: UTC build date string.
    :type date: str
    :param node_version: Node.js runtime version.
    :type node_version: str
    :param raw: Original build dictionary.
    :type raw: dict, optional

    Example::

        >>> BuildInfo("today", "v24.0.0").node_version
        'v24.0.0'
    """

    date: str
    node_version: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        """
        Parse build metadata from a dictionary.

        :param data: Build metadata dictionary.
        :type data: dict
        :return: Parsed build metadata.
        :rtype: BuildInfo

        Example::

            >>> BuildInfo.from_dict({"date": "today", "nodeVersion": "v24"}).node_version
            'v24'
        """

        return cls(
            date=_require(data, "date"),
            node_version=_require(data, "nodeVersion"),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert build metadata to the service DTO shape.

        :return: JSON-serializable build metadata dictionary.
        :rtype: dict

        Example::

            >>> BuildInfo("today", "v24").to_dict()["nodeVersion"]
            'v24'
        """

        return {"date": self.date, "nodeVersion": self.node_version}


@dataclass
class VersionResponse:
    """
    Version response returned by ``GET /v1/version``.

    :param service: Service version metadata.
    :type service: ServiceVersionInfo
    :param upstream: Upstream dependency metadata.
    :type upstream: UpstreamInfo
    :param build: Build metadata.
    :type build: BuildInfo
    :param raw: Original response dictionary.
    :type raw: dict

    Example::

        >>> service = ServiceVersionInfo("svc", "1", "abc", "repo")
        >>> upstream = UpstreamInfo(UpstreamSysML2LSInfo("1", "abc", "pkg", "repo"))
        >>> VersionResponse(service, upstream, BuildInfo("today", "v24"), {}).service.name
        'svc'
    """

    service: ServiceVersionInfo
    upstream: UpstreamInfo
    build: BuildInfo
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        """
        Parse complete version response metadata.

        :param data: Version response dictionary.
        :type data: dict
        :return: Parsed version response.
        :rtype: VersionResponse

        Example::

            >>> data = {"service": {"name": "svc", "version": "1", "revision": "abc", "sourceRepository": "repo"}, "upstream": {"sysml2ls": {"version": "2", "revision": "def", "packageName": "pkg", "repository": "up"}}, "build": {"date": "today", "nodeVersion": "v24"}}
            >>> VersionResponse.from_dict(data).service.version
            '1'
        """

        return cls(
            service=ServiceVersionInfo.from_dict(_dict(data, "service")),
            upstream=UpstreamInfo.from_dict(_dict(data, "upstream")),
            build=BuildInfo.from_dict(_dict(data, "build")),
            raw=dict(data),
        )

    def to_dict(self):
        """
        Convert version response metadata to the service DTO shape.

        :return: JSON-serializable version response dictionary.
        :rtype: dict

        Example::

            >>> service = ServiceVersionInfo("svc", "1", "abc", "repo")
            >>> upstream = UpstreamInfo(UpstreamSysML2LSInfo("2", "def", "pkg", "up"))
            >>> VersionResponse(service, upstream, BuildInfo("today", "v24"), {}).to_dict()["service"]["version"]
            '1'
        """

        return {
            "service": self.service.to_dict(),
            "upstream": self.upstream.to_dict(),
            "build": self.build.to_dict(),
        }
