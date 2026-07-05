"""
Stable exception hierarchy for the Python client.

The module gives callers and the CLI typed failure categories without exposing
raw :mod:`requests`, JSON, or service internals.

The module contains:

* :class:`SysMLClientError` - base class for SDK failures.
* :class:`SysMLServiceError` - HTTP service error with parsed service fields.
* :class:`SysMLDiagnosticsError` - validation diagnostics convenience wrapper.

Example::

    >>> isinstance(SysMLConnectionError("offline"), SysMLClientError)
    True
"""


class SysMLClientError(Exception):
    """
    Base class for client-side SDK exceptions.

    Example::

        >>> isinstance(SysMLClientError("bad"), Exception)
        True
    """


class SysMLConnectionError(SysMLClientError):
    """
    Network, DNS, timeout, refused connection, or local transport error.

    Example::

        >>> str(SysMLConnectionError("offline"))
        'offline'
    """


class SysMLResponseError(SysMLClientError):
    """
    Invalid JSON or malformed response body.

    Example::

        >>> str(SysMLResponseError("bad json"))
        'bad json'
    """


class SysMLServiceError(SysMLClientError):
    """
    HTTP service error returned by ``sysmlv2-ls-service``.

    :param status_code: HTTP status code returned by the service.
    :type status_code: int
    :param error: Stable service error code.
    :type error: str
    :param message: Human-readable service error message.
    :type message: str
    :param issues: Optional schema-validation issues from the service.
    :type issues: object, optional
    :param raw: Parsed or raw service response body.
    :type raw: object, optional

    Example::

        >>> error = SysMLServiceError(400, "bad_request", "bad")
        >>> str(error)
        '400 bad_request: bad'
    """

    def __init__(self, status_code, error, message, issues=None, raw=None):
        super(SysMLServiceError, self).__init__(message)
        self.status_code = status_code
        self.error = error
        self.message = message
        self.issues = issues
        self.raw = raw

    def __str__(self):
        return "%s %s: %s" % (self.status_code, self.error, self.message)


class SysMLValidationLimitError(SysMLClientError):
    """
    Client-side file count, text byte, or body byte preflight failure.

    Example::

        >>> isinstance(SysMLValidationLimitError("too large"), SysMLClientError)
        True
    """


class SysMLDirectoryError(SysMLClientError):
    """
    Directory traversal, include/exclude, symlink, encoding, or boundary error.

    Example::

        >>> isinstance(SysMLDirectoryError("outside root"), SysMLClientError)
        True
    """


class SysMLDiagnosticsError(SysMLClientError):
    """
    Raised when callers choose to turn validation diagnostics into an exception.

    :param result: Validation result whose diagnostics should be exposed.
    :type result: ValidateResult

    Example::

        >>> hasattr(SysMLDiagnosticsError, "__init__")
        True
    """

    def __init__(self, result):
        super(SysMLDiagnosticsError, self).__init__("SysML validation returned errors.")
        self.result = result
        self.diagnostics = result.diagnostics
