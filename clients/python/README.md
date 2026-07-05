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
- `sysmlv2sl` command-line access to the same API surface

`capabilities()` and `refresh_capabilities()` update the cached effective
service limits. Missing or malformed `limits` in a capabilities response raises
`SysMLResponseError`; the client does not silently use old hard-coded defaults.

Runtime dependencies are `requests` and `click`. The package supports Python
3.7, which may force dependency resolution to older `requests` releases. That is
intentional for compatibility; users who keep Python 3.7 accept the associated
security and maintenance risk.

CLI use:

```bash
sysmlv2sl --version
sysmlv2sl -h
sysmlv2sl --base-url http://127.0.0.1:3000 health
sysmlv2sl --base-url http://127.0.0.1:3000 version
sysmlv2sl --base-url http://127.0.0.1:3000 capabilities
sysmlv2sl --base-url http://127.0.0.1:3000 validate text \
  --uri memory:///demo.sysml \
  'package Demo { part def Vehicle; }'
sysmlv2sl --base-url http://127.0.0.1:3000 validate files a.sysml b.sysml
sysmlv2sl --base-url http://127.0.0.1:3000 validate directory . \
  --include '**/*.sysml' \
  --exclude 'vendor/**'
```

Every command and subcommand supports both `-h` and `--help`. Top-level
`-v/--version` prints the client version only. The `version` subcommand calls
the service and prints both client and service metadata. Add top-level `--json`
for machine-readable output and `--pretty` for indented JSON.

Validate commands exit `0` when validation is OK, `1` when the service returns
validation diagnostics with `ok=false`, `2` for CLI usage errors, and `3` for
connection, service, response, directory, or client preflight errors.

Test dependencies are available through the `test` extra.

```bash
python -m pip install -e "clients/python[test]"
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
cd clients/python
python -m coverage run --branch -m pytest
python -m coverage report --fail-under=100
```

This repository currently has no root `LICENSE` file and no `license` field in
`package.json`, so this package does not declare an independent license.
