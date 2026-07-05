# Quickstart

Initialize the repository and build the pinned upstream packages:

```bash
git submodule update --init --recursive
corepack enable
pnpm install --frozen-lockfile
pnpm run build:upstream
pnpm run ci
```

Start the service:

```bash
pnpm run dev
```

Validate one SysML document:

```bash
curl -sS -X POST http://127.0.0.1:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///demo.sysml","text":"package Demo { part def Vehicle; }"}]}'
```

Use the Python CLI after installing the client:

```bash
python -m pip install -e "clients/python[test]"
sysmlv2sl validate text 'package Demo { part def Vehicle; }'
```
