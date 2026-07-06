# Python install

The Python client lives in `clients/python` and installs a top-level module named `sysmlv2slclient` plus a `sysmlv2sl` command-line entry point.

## Install from this repository

For local development:

```bash
python -m pip install -e "clients/python[test]"
```

For a non-editable install from a checkout:

```bash
python -m pip install ./clients/python
```

Verify the import and CLI:

```bash
python - <<'PY'
from sysmlv2slclient import SysMLV2LSClient, __version__
print(__version__)
print(SysMLV2LSClient)
PY
sysmlv2sl --version
sysmlv2sl -h
```

## Python version and dependencies

| Item            | Policy                                                                   |
| --------------- | ------------------------------------------------------------------------ |
| Python runtime  | Client supports Python 3.7+.                                             |
| HTTP dependency | `requests` is used directly.                                             |
| CLI dependency  | `click` provides command groups and help.                                |
| Tests           | `pytest`, `coverage`, and `ruff` are available through the `test` extra. |

!!! warning "Python 3.7 dependency risk"
Python 3.7 can force dependency resolution to older `requests` lines because newer `requests` releases require newer Python versions. The repository documents this compatibility tradeoff; callers who force old dependency versions accept the associated security and maintenance risk.

## Development checks

```bash
python -m ruff format --check clients/python/src clients/python/tests scripts/check-python-docs.py
python -m ruff check clients/python/src clients/python/tests scripts/check-python-docs.py
python scripts/check-python-docs.py
cd clients/python
python -m coverage run --branch -m pytest
python -m coverage report --fail-under=100
```

The client must maintain 100% branch coverage. Public docstrings must include `Example::` blocks and reStructuredText-style parameter, return, and raise documentation.

## Relationship to `examples/python`

`examples/python` remains a standard-library smoke example for users who do not want to install the SDK. Do not move the example into `clients/python`, and do not make the example depend on the package unless the repository explicitly changes that policy.
