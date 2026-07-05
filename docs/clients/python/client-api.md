# Python API

Use `SysMLV2LSClient` with a service base URL:

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text("package Demo { part def Vehicle; }")
print(result.ok)
```

API reference is generated from the package docstrings in [Python reference](../../reference/python/index.md).
