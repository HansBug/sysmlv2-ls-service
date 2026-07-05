# Local development

Required tools:

- Node.js `>=20.19` for local development.
- pnpm `9.15.4` via Corepack.
- Python for the optional client and docs tooling.

Common checks:

```bash
pnpm run format:check
pnpm run comments:check
pnpm run ci
pnpm run audit
```

Documentation checks are separate from service/client CI:

```bash
python -m pip install -r docs/requirements.txt
python -m pip install -e clients/python
pnpm run docs:check:base
pnpm run docs:check:full
```
