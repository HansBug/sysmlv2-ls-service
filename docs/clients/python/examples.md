# Python examples

These examples assume the service is running at `http://127.0.0.1:3000`.

## Validate one string

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)
print(result.ok)
```

## Validate a multi-file workspace

```python
from sysmlv2slclient import SysMLFile, SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
files = [
    SysMLFile("package Library { part def Vehicle; }", uri="memory:///library.sysml"),
    SysMLFile(
        "package Model { public import Library::*; part car : Vehicle; }",
        uri="memory:///model.sysml",
    ),
]
result = client.validate_files(files)
print(result.ok)
```

## Validate a directory

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_directory(
    "models",
    include=("**/*.sysml", "**/*.kerml"),
    exclude=("vendor/**", "generated/**"),
)
print(result.ok)
```

Use `uri_scheme="file"` only when sending absolute local file paths is acceptable for the service environment. The default memory URI mode is more portable for remote services and CI jobs.

## Print diagnostics compactly

```python
result = client.validate_text(
    "package Broken { part def }",
    uri="memory:///broken.sysml",
)
for diagnostic in result.diagnostics:
    start = diagnostic.range.start
    print(
        diagnostic.severity,
        diagnostic.code,
        "%s:%s:%s" % (diagnostic.uri, start.line, start.character),
        diagnostic.message,
    )
```

Representative output shape:

```text
error parsing-error memory:///broken.sysml:0:26 Expecting: one of these possible Token sequences: ...
```

Exact parser wording comes from upstream Langium/Chevrotain and may change with the pinned upstream submodule.

## CLI equivalents

```bash
sysmlv2sl validate text 'package Demo { part def Vehicle; }'
sysmlv2sl validate files library.sysml model.sysml
sysmlv2sl validate directory models --include '**/*.sysml' --exclude 'vendor/**'
sysmlv2sl --json --pretty validate text 'package Broken { part def }'
```
