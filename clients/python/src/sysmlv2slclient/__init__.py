"""
Typed Python client exports for ``sysmlv2-ls-service``.

This package exposes the installable SDK surface for Python callers. The table
below is the module roadmap used by humans and LLM agents when deciding which
object to import.

Module roadmap
==============

+-------------------------------+-------------------------------------------+
| Export                        | Purpose                                   |
+===============================+===========================================+
| :class:`SysMLV2LSClient`      | Calls service health, version,            |
|                               | capabilities, and validation endpoints.   |
+-------------------------------+-------------------------------------------+
| :class:`SysMLFile`            | Represents one request-local SysML/KerML  |
|                               | document submitted to validation.         |
+-------------------------------+-------------------------------------------+
| ``*Response`` classes         | Parse and expose service-owned response   |
|                               | DTOs without leaking upstream internals.  |
+-------------------------------+-------------------------------------------+
| ``*Error`` classes            | Provide stable client-side exception      |
|                               | categories for callers and CLI handling.  |
+-------------------------------+-------------------------------------------+

Example::

    >>> from sysmlv2slclient import SysMLV2LSClient
    >>> client = SysMLV2LSClient("http://127.0.0.1:3000", limits=None)
    >>> callable(client.health)
    True
"""

from ._version import __service_api_version__, __version__
from .client import SysMLV2LSClient
from .errors import (
    SysMLClientError,
    SysMLConnectionError,
    SysMLDiagnosticsError,
    SysMLDirectoryError,
    SysMLResponseError,
    SysMLServiceError,
    SysMLValidationLimitError,
)
from .models import (
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
    SysMLFile,
    UpstreamInfo,
    UpstreamSysML2LSInfo,
    ValidateLimits,
    ValidateMeta,
    ValidateResult,
    VersionResponse,
)

__all__ = [
    "__service_api_version__",
    "__version__",
    "BuildInfo",
    "CapabilitiesResponse",
    "Diagnostic",
    "FileValidationSummary",
    "HealthResponse",
    "HttpLimits",
    "LanguageInfo",
    "ServiceLimits",
    "ServiceVersionInfo",
    "SourcePosition",
    "SourceRange",
    "SysMLClientError",
    "SysMLConnectionError",
    "SysMLDiagnosticsError",
    "SysMLDirectoryError",
    "SysMLFile",
    "SysMLResponseError",
    "SysMLServiceError",
    "SysMLV2LSClient",
    "SysMLValidationLimitError",
    "UpstreamInfo",
    "UpstreamSysML2LSInfo",
    "ValidateLimits",
    "ValidateMeta",
    "ValidateResult",
    "VersionResponse",
]
