# sysmlv2slclient

Python client for `sysmlv2-ls-service`.

Install from this repository:

```bash
python -m pip install ./clients/python
```

Basic use:

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)
print(result.ok)
```

The `base_url` should be the service root URL. Query strings and fragments are
rejected. Path prefixes are preserved for reverse-proxy deployments.

The client supports:

- `health()`
- `capabilities()`
- `version()`
- `validate_text()`
- `validate_files()`
- `validate_directory()`

`capabilities()` and `refresh_capabilities()` update the cached effective
service limits. Missing or malformed `limits` in a capabilities response raises
`SysMLResponseError`; the client does not silently use old hard-coded defaults.

Runtime dependencies are intentionally empty. Test dependencies are available
through the `test` extra.

```bash
python -m pip install -e "clients/python[test]"
cd clients/python
python -m coverage run --branch -m pytest
python -m coverage report --fail-under=100
```

This repository currently has no root `LICENSE` file and no `license` field in
`package.json`, so this package does not declare an independent license.
