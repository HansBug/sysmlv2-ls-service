# Python errors

Client-side exceptions inherit from `SysMLClientError`. Service HTTP errors are represented by `SysMLServiceError`, malformed response bodies by `SysMLResponseError`, transport failures by `SysMLConnectionError`, directory collection failures by `SysMLDirectoryError`, and client-side limit preflight failures by `SysMLValidationLimitError`.
