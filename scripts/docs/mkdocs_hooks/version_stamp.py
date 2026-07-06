"""MkDocs hooks for version metadata and Python API rendering polish."""

from __future__ import annotations

import datetime as _dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict


_SPHINX_ROLE_RE = re.compile(
    r":(?:class|func|meth|mod|attr|exc|data|obj):<code>(?P<target>[^<]+)</code>"
)


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


def _normalize_python_reference_rest(content: str) -> str:
    """Normalize reStructuredText fragments left in mkdocstrings HTML output."""

    content = _SPHINX_ROLE_RE.sub(r"<code>\g<target></code>", content)
    content = re.sub(
        r"<p>Examples?::</p>\s*(<pre><code>)",
        r'<p><strong>Example</strong></p>\n\1',
        content,
    )
    return content


def on_page_content(html: str, page: Any, config: Dict[str, Any], files: Any) -> str:
    """Post-process generated Python API HTML so Sphinx/reST docstrings render cleanly."""

    if getattr(page, "url", "") == "reference/python/":
        return _normalize_python_reference_rest(html)
    return html
