#!/usr/bin/env python3
"""Call sysmlv2-ls-service with intentionally flawed SysML v2 examples.

Usage:
  SYSMLV2_LS_URL=http://127.0.0.1:3000 python examples/python/validate_example.py
  python examples/python/validate_example.py --url http://127.0.0.1:3000 --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


DEFAULT_URL = os.environ.get("SYSMLV2_LS_URL", "http://127.0.0.1:3000")


REQUEST: dict[str, Any] = {
    "files": [
        {
            "uri": "memory:///broken-semantic.sysml",
            "text": """package BrokenSemantic {
    part def Vehicle;
    part def Vehicle;
    public import Missing::*;
    part loose;
    part missing : MissingType;
}""",
        },
        {
            "uri": "memory:///broken-syntax.sysml",
            "text": "package BrokenSyntax { part def }",
        },
    ],
    "standardLibrary": "none",
    "validationChecks": "all",
}


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{url.rstrip('/')}/v1/validate",
        data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise SystemExit(
            f"HTTP {error.code}: {error.read().decode('utf-8', errors='replace')}"
        ) from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Could not connect to {url}: {error.reason}") from error


def print_table(result: dict[str, Any]) -> None:
    print(f"ok: {result.get('ok')}")
    print(f"elapsedMs: {result.get('meta', {}).get('elapsedMs')}")
    print()
    print("Files:")
    for file in result.get("files", []):
        print(
            f"- {file['uri']} "
            f"language={file['language']} "
            f"parserErrors={file['parserErrors']} "
            f"lexerErrors={file['lexerErrors']} "
            f"diagnostics={file['diagnostics']}"
        )
    print()
    print("Diagnostics:")
    for index, diagnostic in enumerate(result.get("diagnostics", []), start=1):
        start = diagnostic["range"]["start"]
        first_message_line = (diagnostic.get("message", "").splitlines() or [""])[0]
        print(
            f"{index}. {diagnostic['severity']} "
            f"{diagnostic.get('code', '<no-code>')} "
            f"{diagnostic['uri']}:{start['line'] + 1}:{start['character'] + 1}"
        )
        print(f"   {first_message_line}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL, help="Base service URL")
    parser.add_argument("--json", action="store_true", help="Print raw JSON response")
    args = parser.parse_args()

    result = post_json(args.url, REQUEST)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_table(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
