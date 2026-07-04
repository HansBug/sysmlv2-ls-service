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
        return cls(
            text=_require(data, "text"),
            uri=data.get("uri"),
            path=data.get("path"),
            language=data.get("language"),
        )

    def to_dict(self):
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
    line: int
    character: int

    @classmethod
    def from_dict(cls, data):
        return cls(line=_require(data, "line"), character=_require(data, "character"))

    def to_dict(self):
        return {"line": self.line, "character": self.character}


@dataclass
class SourceRange:
    start: SourcePosition
    end: SourcePosition

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=SourcePosition.from_dict(_dict(data, "start")),
            end=SourcePosition.from_dict(_dict(data, "end")),
        )

    def to_dict(self):
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Diagnostic:
    severity: str
    source: str
    message: str
    uri: str
    range: SourceRange
    code: Optional[Union[str, int]] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
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
    uri: str
    language: str
    parser_errors: int
    lexer_errors: int
    diagnostics: int
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            uri=_require(data, "uri"),
            language=_require(data, "language"),
            parser_errors=_require(data, "parserErrors"),
            lexer_errors=_require(data, "lexerErrors"),
            diagnostics=_require(data, "diagnostics"),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "uri": self.uri,
            "language": self.language,
            "parserErrors": self.parser_errors,
            "lexerErrors": self.lexer_errors,
            "diagnostics": self.diagnostics,
        }


@dataclass
class ValidateMeta:
    standard_library: str
    validation_checks: str
    elapsed_ms: float
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            standard_library=_require(data, "standardLibrary"),
            validation_checks=_require(data, "validationChecks"),
            elapsed_ms=_require(data, "elapsedMs"),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "standardLibrary": self.standard_library,
            "validationChecks": self.validation_checks,
            "elapsedMs": self.elapsed_ms,
        }


@dataclass
class ValidateResult:
    ok: bool
    diagnostics: List[Diagnostic]
    files: List[FileValidationSummary]
    meta: ValidateMeta
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
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
        errors = []
        for item in self.diagnostics:
            if item.severity == "error":
                errors.append(item)
        return errors

    @property
    def warnings(self):
        warnings = []
        for item in self.diagnostics:
            if item.severity == "warning":
                warnings.append(item)
        return warnings

    def diagnostics_by_file(self):
        grouped = {}
        for diagnostic in self.diagnostics:
            grouped.setdefault(diagnostic.uri, []).append(diagnostic)
        return grouped

    def raise_for_diagnostics(self):
        if not self.ok or self.errors:
            raise SysMLDiagnosticsError(self)
        return None

    def to_dict(self):
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
    ok: bool
    service: str
    version: str
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        return cls(
            ok=_require(data, "ok"),
            service=_require(data, "service"),
            version=_require(data, "version"),
            raw=dict(data),
        )

    def to_dict(self):
        return {"ok": self.ok, "service": self.service, "version": self.version}


@dataclass
class LanguageInfo:
    id: str
    extensions: List[str]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(id=_require(data, "id"), extensions=_list(data, "extensions"), raw=dict(data))

    def to_dict(self):
        return {"id": self.id, "extensions": list(self.extensions)}


@dataclass
class ValidateLimits:
    max_files: Optional[int]
    max_file_text_bytes: Optional[int]
    max_total_text_bytes: Optional[int]
    validation_timeout_ms: Optional[int]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            max_files=_require(data, "maxFiles"),
            max_file_text_bytes=_require(data, "maxFileTextBytes"),
            max_total_text_bytes=_require(data, "maxTotalTextBytes"),
            validation_timeout_ms=_require(data, "validationTimeoutMs"),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "maxFiles": self.max_files,
            "maxFileTextBytes": self.max_file_text_bytes,
            "maxTotalTextBytes": self.max_total_text_bytes,
            "validationTimeoutMs": self.validation_timeout_ms,
        }


@dataclass
class HttpLimits:
    body_limit_bytes: Optional[int]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(body_limit_bytes=_require(data, "bodyLimitBytes"), raw=dict(data))

    def to_dict(self):
        return {"bodyLimitBytes": self.body_limit_bytes}


@dataclass
class ServiceLimits:
    validate: ValidateLimits
    http: HttpLimits
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            validate=ValidateLimits.from_dict(_dict(data, "validate")),
            http=HttpLimits.from_dict(_dict(data, "http")),
            raw=dict(data),
        )

    def to_dict(self):
        return {"validate": self.validate.to_dict(), "http": self.http.to_dict()}


@dataclass
class CapabilitiesResponse:
    languages: List[LanguageInfo]
    validation_checks: List[str]
    standard_library: List[str]
    limits: ServiceLimits
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
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
    name: str
    version: str
    revision: str
    source_repository: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=_require(data, "name"),
            version=_require(data, "version"),
            revision=_require(data, "revision"),
            source_repository=_require(data, "sourceRepository"),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "revision": self.revision,
            "sourceRepository": self.source_repository,
        }


@dataclass
class UpstreamSysML2LSInfo:
    version: str
    revision: str
    package_name: str
    repository: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            version=_require(data, "version"),
            revision=_require(data, "revision"),
            package_name=_require(data, "packageName"),
            repository=_require(data, "repository"),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "version": self.version,
            "revision": self.revision,
            "packageName": self.package_name,
            "repository": self.repository,
        }


@dataclass
class UpstreamInfo:
    sysml2ls: UpstreamSysML2LSInfo
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            sysml2ls=UpstreamSysML2LSInfo.from_dict(_dict(data, "sysml2ls")),
            raw=dict(data),
        )

    def to_dict(self):
        return {"sysml2ls": self.sysml2ls.to_dict()}


@dataclass
class BuildInfo:
    date: str
    node_version: str
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            date=_require(data, "date"),
            node_version=_require(data, "nodeVersion"),
            raw=dict(data),
        )

    def to_dict(self):
        return {"date": self.date, "nodeVersion": self.node_version}


@dataclass
class VersionResponse:
    service: ServiceVersionInfo
    upstream: UpstreamInfo
    build: BuildInfo
    raw: Dict[str, Any]

    @classmethod
    def from_dict(cls, data):
        return cls(
            service=ServiceVersionInfo.from_dict(_dict(data, "service")),
            upstream=UpstreamInfo.from_dict(_dict(data, "upstream")),
            build=BuildInfo.from_dict(_dict(data, "build")),
            raw=dict(data),
        )

    def to_dict(self):
        return {
            "service": self.service.to_dict(),
            "upstream": self.upstream.to_dict(),
            "build": self.build.to_dict(),
        }
