"""MkDocs hook that appends build/version metadata to documentation pages."""

from __future__ import annotations

import datetime as _dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict


def _run_git(args: list[str], fallback: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return fallback


def _source_date() -> str:
    timestamp = _run_git(["show", "-s", "--format=%ct", "HEAD"], "")
    if timestamp.isdigit():
        return _dt.datetime.fromtimestamp(int(timestamp), tz=_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    return "unknown"


def _load_stamp(config: Dict[str, Any]) -> Dict[str, Any]:
    docs_dir = Path(config["docs_dir"])
    stamp_path = docs_dir / "_data" / "version.json"
    return json.loads(stamp_path.read_text(encoding="utf-8"))


def on_page_markdown(markdown: str, page: Any, config: Dict[str, Any], files: Any) -> str:
    """Append a standard version block unless page front matter opts out."""

    if getattr(page, "meta", {}).get("hide_version_stamp"):
        return markdown

    stamp = _load_stamp(config)
    service = stamp["service"]
    upstream = stamp["upstream"]["sysml2ls"]
    revision = _run_git(["rev-parse", "--short=12", "HEAD"], "unknown")
    source_date = _source_date()
    block = f"""

---

!!! info "Version metadata"
    Service version: `{service['version']}` · repository revision: `{revision}` · upstream `sysml-2ls`: `{upstream['version']}` / `{upstream['revision'][:12]}` · docs source date: `{source_date}`.
"""
    return markdown.rstrip() + block + "\n"
