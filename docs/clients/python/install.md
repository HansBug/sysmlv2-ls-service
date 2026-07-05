# Python install

Install the client in editable mode for development:

```bash
python -m pip install -e "clients/python[test]"
```

The top-level module is `sysmlv2slclient`; the CLI entry point is `sysmlv2sl`.

The client intentionally uses `requests`. Low-version `requests` risk is documented in the client README; callers who force older dependency versions accept that risk.
