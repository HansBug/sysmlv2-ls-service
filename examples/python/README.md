# Python Validation Example

This example submits intentionally flawed SysML v2 text to
`sysmlv2-ls-service` and prints a diagnostics table.

It uses only Python standard-library modules.

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000
```

The example submits two broken in-memory files. The semantic example has a
missing import, duplicate declarations, and untyped part usages:

```sysml
package BrokenSemantic {
    part def Vehicle;
    part def Vehicle;
    public import Missing::*;
    part loose;
    part missing : MissingType;
}
```

The syntax example is intentionally incomplete:

```sysml
package BrokenSyntax { part def }
```

Expected console shape:

```text
ok: False
elapsedMs: <varies>

Files:
- memory:///broken-semantic.sysml language=sysml parserErrors=0 lexerErrors=0 diagnostics=9
- memory:///broken-syntax.sysml language=sysml parserErrors=1 lexerErrors=0 diagnostics=1

Diagnostics:
1. error linking-error memory:///broken-semantic.sysml:4:19
   Could not resolve reference to Namespace named 'Missing'.
2. error linking-error memory:///broken-semantic.sysml:4:19
   Could not resolve reference to Namespace named 'Missing'.
3. error linking-error memory:///broken-semantic.sysml:6:20
   Could not resolve reference to Type named 'MissingType'.
4. warning validateNamespaceDistinguishability memory:///broken-semantic.sysml:2:14
   Duplicate of another member named Vehicle.
5. warning validateNamespaceDistinguishability memory:///broken-semantic.sysml:3:14
   Duplicate of another member named Vehicle.
6. error validateFeatureTyping memory:///broken-semantic.sysml:5:5
   A Feature must be typed by at least one type.
7. error validatePartUsagePartDefinition memory:///broken-semantic.sysml:5:5
   At least one of the itemDefinitions of a PartUsage must be a PartDefinition.
8. error validateFeatureTyping memory:///broken-semantic.sysml:6:20
   A Feature must be typed by at least one type.
9. error validatePartUsagePartDefinition memory:///broken-semantic.sysml:6:5
   At least one of the itemDefinitions of a PartUsage must be a PartDefinition.
10. error parsing-error memory:///broken-syntax.sysml:1:33
   Expecting: one of these possible Token sequences:
```

Use `--json` to print the raw `/v1/validate` response.

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000 --json
```
