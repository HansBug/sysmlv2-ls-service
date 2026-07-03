# Python Validation Example

This example submits intentionally flawed SysML v2 text to
`sysmlv2-ls-service` and prints a diagnostics table.

It uses only Python standard-library modules.

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000
```

Use `--json` to print the raw `/v1/validate` response.

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000 --json
```

See the root `README.md` for the exact SysML input and expected console shape.
