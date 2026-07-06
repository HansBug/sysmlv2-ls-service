# Clients

This repository currently ships one installable client under `clients/python` and keeps `examples/python` as a separate standard-library smoke example. The client tree is intentionally separate from examples so future language clients can be added under `clients/<language>` without changing the service API boundary.

## Client inventory

| Client | Package/module    | CLI         | Status      | Docs                                                                            |
| ------ | ----------------- | ----------- | ----------- | ------------------------------------------------------------------------------- |
| Python | `sysmlv2slclient` | `sysmlv2sl` | implemented | [Install](python/install.md), [API](python/client-api.md), [CLI](python/cli.md) |

## Design principles for clients

- Keep the HTTP service DTO boundary intact; do not expose Langium or upstream object shapes.
- Support all implemented service endpoints: health, capabilities, version, and validate.
- Make multi-file validation easy through explicit file DTOs and directory collection helpers.
- Preserve service diagnostics as data rather than converting validation failures into transport errors.
- Provide automation-friendly JSON output for CLI users and LLM agents.
- Keep examples in `examples/` independent from installable clients.

## Python quick example

```python
from sysmlv2slclient import SysMLV2LSClient

client = SysMLV2LSClient("http://127.0.0.1:3000")
result = client.validate_text(
    "package Demo { part def Vehicle; }",
    uri="memory:///demo.sysml",
)
print(result.ok)
```
