import os
import re
from pathlib import Path
from urllib.parse import quote

from .errors import SysMLDirectoryError
from .models import SysMLFile


def _as_sequence(value, default):
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _validate_pattern(pattern):
    if os.path.isabs(pattern):
        raise SysMLDirectoryError("Glob pattern must be relative: %s" % pattern)
    parts = pattern.replace("\\", "/").split("/")
    if "." in parts or ".." in parts:
        raise SysMLDirectoryError("Glob pattern cannot contain . or .. segments: %s" % pattern)


def _glob_to_regex(pattern):
    _validate_pattern(pattern)
    parts = pattern.replace("\\", "/").split("/")
    regex = "^"
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        if part == "**":
            regex += ".*" if last else "(?:[^/]+/)*"
            continue
        segment = ""
        for char in part:
            if char == "*":
                segment += "[^/]*"
            elif char == "?":
                segment += "[^/]"
            else:
                segment += re.escape(char)
        regex += segment
        if not last:
            regex += "/"
    regex += "$"
    return re.compile(regex)


def _matcher(rule, default):
    if callable(rule):
        return rule
    patterns = _as_sequence(rule, default)
    compiled = [_glob_to_regex(pattern) for pattern in patterns]

    def matches(rel_path):
        rel = rel_path.as_posix()
        return any(pattern.match(rel) for pattern in compiled)

    return matches


def _inside(root, resolved):
    try:
        return os.path.commonpath([str(root), str(resolved)]) == str(root)
    except ValueError:
        return False


def _scan(root, follow_symlinks):
    files = []
    visited = set()

    def scan_dir(directory):
        stat = os.stat(str(directory))
        identity = (stat.st_dev, stat.st_ino)
        if identity in visited:
            raise SysMLDirectoryError("Symlink loop detected: %s" % directory)
        visited.add(identity)

        with os.scandir(str(directory)) as entries:
            for entry in entries:
                entry_path = Path(entry.path)
                if entry.is_symlink():
                    if not follow_symlinks:
                        continue
                    resolved = entry_path.resolve(strict=True)
                    if not _inside(root, resolved):
                        raise SysMLDirectoryError("Symlink target escapes root: %s" % entry_path)
                    if resolved.is_dir():
                        scan_dir(resolved)
                    elif resolved.is_file():
                        files.append((entry_path, resolved))
                    continue
                if entry.is_dir(follow_symlinks=False):
                    scan_dir(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    resolved = entry_path.resolve(strict=True)
                    if not _inside(root, resolved):
                        raise SysMLDirectoryError("File escapes root: %s" % entry_path)
                    files.append((entry_path, resolved))

        visited.remove(identity)

    scan_dir(root)
    return files


def _memory_uri(root, rel_posix, relative_uris):
    segments = rel_posix.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        raise SysMLDirectoryError("Invalid relative path for memory URI: %s" % rel_posix)
    encoded = "/".join(quote(segment, safe="") for segment in segments)
    if relative_uris:
        return "memory:///%s" % encoded
    root_name = quote(root.name or "workspace", safe="")
    return "memory:///%s/%s" % (root_name, encoded)


def collect_directory_files(
    path,
    include=("**/*.sysml",),
    exclude=None,
    uri_scheme="memory",
    relative_uris=True,
    language=None,
    encoding="utf-8",
    encoding_errors="strict",
    follow_symlinks=False,
):
    try:
        root = Path(path).resolve(strict=True)
    except OSError as error:
        raise SysMLDirectoryError("Path does not exist: %s" % error)
    if not root.is_dir():
        raise SysMLDirectoryError("Path is not a directory: %s" % path)
    if uri_scheme not in ("memory", "file"):
        raise SysMLDirectoryError("uri_scheme must be 'memory' or 'file'")
    if uri_scheme == "file" and relative_uris:
        raise SysMLDirectoryError("file uri_scheme requires relative_uris=False")
    if language is not None and language not in ("sysml", "kerml"):
        raise ValueError("language must be 'sysml' or 'kerml'")

    include_matcher = _matcher(include, ("**/*.sysml",))
    exclude_matcher = _matcher(exclude, ())
    selected = []

    for display_path, resolved_path in _scan(root, follow_symlinks):
        rel_posix = Path(os.path.relpath(str(display_path), str(root))).as_posix()
        rel_path = Path(rel_posix)
        if not include_matcher(rel_path):
            continue
        if exclude_matcher(rel_path):
            continue
        selected.append((rel_posix, resolved_path))

    if not selected:
        raise SysMLDirectoryError("No files matched directory validation input.")

    files = []
    seen_uris = set()
    for rel_posix, resolved_path in sorted(selected, key=lambda item: item[0]):
        try:
            text = resolved_path.read_text(encoding=encoding, errors=encoding_errors)
        except UnicodeDecodeError as error:
            raise SysMLDirectoryError("Cannot decode %s: %s" % (rel_posix, error))

        if uri_scheme == "memory":
            uri = _memory_uri(root, rel_posix, relative_uris)
            if uri in seen_uris:
                raise SysMLDirectoryError("Duplicate generated URI: %s" % uri)
            seen_uris.add(uri)
            files.append(SysMLFile(uri=uri, text=text, language=language))
        else:
            files.append(SysMLFile(path=str(resolved_path), text=text, language=language))

    return files
