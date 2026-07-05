# Python examples

Validate a directory as one request-local workspace:

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_directory(".", include=("**/*.sysml",), exclude=("vendor/**",))
print(result.ok)
```

Use `uri_scheme="file"` only when the service can interpret those file paths. The default memory URI mode is preferred for portable requests.
