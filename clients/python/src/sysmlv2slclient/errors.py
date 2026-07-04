class SysMLClientError(Exception):
    """Base client-side exception."""


class SysMLConnectionError(SysMLClientError):
    """Network, DNS, timeout, refused connection, or local transport error."""


class SysMLResponseError(SysMLClientError):
    """Invalid JSON or malformed response body."""


class SysMLServiceError(SysMLClientError):
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
    """Client-side file count, text byte, or body byte preflight failure."""


class SysMLDirectoryError(SysMLClientError):
    """Directory traversal, include/exclude, symlink, encoding, or boundary error."""


class SysMLDiagnosticsError(SysMLClientError):
    def __init__(self, result):
        super(SysMLDiagnosticsError, self).__init__("SysML validation returned errors.")
        self.result = result
        self.diagnostics = result.diagnostics
