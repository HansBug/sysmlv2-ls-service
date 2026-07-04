import os
from pathlib import Path

import pytest

from sysmlv2slclient import SysMLDirectoryError, SysMLV2LSClient
import sysmlv2slclient.directory as directory
from sysmlv2slclient.directory import (
    _append_file_if_regular,
    _glob_to_regex,
    _matcher,
    _memory_uri,
    _scan,
    collect_directory_files,
)

from test_client import FakeOpener, capabilities_body, validate_body


def write(path, text, encoding="utf-8"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)


def test_default_directory_collection_and_memory_uris(tmp_path):
    write(tmp_path / "a.sysml", "package A {}")
    write(tmp_path / "nested" / "b.sysml", "package B {}")
    write(tmp_path / "nested" / "c.kerml", "package C {}")
    files = collect_directory_files(tmp_path)

    assert [item.uri for item in files] == [
        "memory:///a.sysml",
        "memory:///nested/b.sysml",
    ]
    assert [item.text for item in files] == ["package A {}", "package B {}"]


def test_include_exclude_callable_and_root_prefix(tmp_path):
    write(tmp_path / "keep.sysml", "package Keep {}")
    write(tmp_path / "skip.sysml", "package Skip {}")
    write(tmp_path / "kernel.kerml", "package Kernel {}")

    files = collect_directory_files(
        tmp_path,
        include=lambda rel: rel.suffix in (".sysml", ".kerml"),
        exclude=lambda rel: rel.name.startswith("skip"),
        relative_uris=False,
        language="kerml",
    )

    assert [item.uri for item in files] == [
        "memory:///%s/keep.sysml" % tmp_path.name,
        "memory:///%s/kernel.kerml" % tmp_path.name,
    ]
    assert all(item.language == "kerml" for item in files)


def test_glob_include_and_exclude_patterns(tmp_path):
    write(tmp_path / "a.sysml", "package A {}")
    write(tmp_path / "vendor" / "b.sysml", "package B {}")
    write(tmp_path / ".generated" / "c.sysml", "package C {}")
    files = collect_directory_files(
        tmp_path,
        include=("**/*.sysml",),
        exclude=("vendor/**", "**/.generated/**"),
    )
    assert [item.uri for item in files] == ["memory:///a.sysml"]


def test_file_scheme_and_validation_wrapper(tmp_path):
    write(tmp_path / "a.sysml", "package A {}")
    files = collect_directory_files(tmp_path, uri_scheme="file", relative_uris=False)
    assert files[0].path == str((tmp_path / "a.sysml").resolve())

    opener = FakeOpener([capabilities_body(1000), validate_body()])
    result = SysMLV2LSClient("http://example.test", opener=opener).validate_directory(tmp_path)
    assert result.ok is True


def test_directory_errors(tmp_path):
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path / "missing")
    file_path = tmp_path / "file.sysml"
    write(file_path, "package File {}")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(file_path)
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, include="/abs/*.sysml")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, include="../*.sysml")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, uri_scheme="file")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, uri_scheme="bad", relative_uris=False)
    with pytest.raises(ValueError):
        collect_directory_files(tmp_path, language="bad")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(empty)


def test_encoding_and_special_uri_characters(tmp_path):
    special = tmp_path / "space #?%" / "非ascii.sysml"
    write(special, "package Special {}")
    files = collect_directory_files(tmp_path)
    assert files[0].uri == "memory:///space%20%23%3F%25/%E9%9D%9Eascii.sysml"

    bad = tmp_path / "bad.sysml"
    bad.write_bytes(b"\xff")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, include="bad.sysml")
    assert collect_directory_files(tmp_path, include="bad.sysml", encoding_errors="ignore")[0].text == ""


def test_symlink_policy(tmp_path):
    target = tmp_path / "target.sysml"
    write(target, "package Target {}")
    link = tmp_path / "link.sysml"
    link.symlink_to(target)
    empty_dir = tmp_path / "empty-dir"
    empty_dir.mkdir()
    empty_dir_link = tmp_path / "empty-dir-link"
    empty_dir_link.symlink_to(empty_dir, target_is_directory=True)
    assert [item.uri for item in collect_directory_files(tmp_path)] == ["memory:///target.sysml"]
    assert [item.uri for item in collect_directory_files(tmp_path, follow_symlinks=True)] == [
        "memory:///link.sysml",
        "memory:///target.sysml",
    ]

    outside = tmp_path.parent / "outside.sysml"
    write(outside, "package Outside {}")
    outside_link = tmp_path / "outside.sysml"
    outside_link.symlink_to(outside)
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, follow_symlinks=True)


def test_internal_symlink_directory_is_deduplicated(tmp_path):
    real_dir = tmp_path / "real"
    write(real_dir / "a.sysml", "package A {}")
    alias = tmp_path / "alias"
    alias.symlink_to(real_dir, target_is_directory=True)

    files = collect_directory_files(tmp_path, follow_symlinks=True)
    assert [(item.uri, item.path) for item in files] == [("memory:///real/a.sysml", None)]

    file_scheme_files = collect_directory_files(
        tmp_path,
        follow_symlinks=True,
        uri_scheme="file",
        relative_uris=False,
    )
    assert [(item.uri, item.path) for item in file_scheme_files] == [
        (None, str((real_dir / "a.sysml").resolve()))
    ]


def test_file_scheme_deduplicates_file_symlink_paths(tmp_path):
    target = tmp_path / "target.sysml"
    write(target, "package Target {}")
    link = tmp_path / "link.sysml"
    link.symlink_to(target)

    files = collect_directory_files(
        tmp_path,
        follow_symlinks=True,
        uri_scheme="file",
        relative_uris=False,
    )

    assert [item.path for item in files] == [str(target.resolve())]


def test_broken_symlink_reports_directory_error(tmp_path):
    write(tmp_path / "a.sysml", "package A {}")
    broken = tmp_path / "broken.sysml"
    broken.symlink_to(tmp_path / "missing.sysml")

    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, follow_symlinks=True)


def test_scan_wraps_os_errors(tmp_path, monkeypatch):
    root = tmp_path.resolve()

    def broken_stat(path):
        raise OSError("stat failed")

    monkeypatch.setattr(directory.os, "stat", broken_stat)
    with pytest.raises(SysMLDirectoryError):
        _scan(root, follow_symlinks=False)
    monkeypatch.undo()

    def broken_scandir(path):
        raise OSError("scan failed")

    monkeypatch.setattr(directory.os, "scandir", broken_scandir)
    with pytest.raises(SysMLDirectoryError):
        _scan(root, follow_symlinks=False)
    monkeypatch.undo()

    file_path = tmp_path / "a.sysml"
    write(file_path, "package A {}")
    original_resolve = directory.Path.resolve

    def broken_file_resolve(self, strict=False):
        if self.name == "a.sysml":
            raise OSError("resolve failed")
        return original_resolve(self, strict=strict)

    monkeypatch.setattr(directory.Path, "resolve", broken_file_resolve)
    with pytest.raises(SysMLDirectoryError):
        _scan(root, follow_symlinks=False)


def test_non_regular_entries_and_boundary_defense(tmp_path, monkeypatch):
    write(tmp_path / "a.sysml", "package A {}")
    fifo = tmp_path / "pipe.sysml"
    os.mkfifo(str(fifo))
    fifo_target = tmp_path / "pipe-target"
    os.mkfifo(str(fifo_target))
    fifo_link = tmp_path / "pipe-link.sysml"
    fifo_link.symlink_to(fifo_target)
    files = collect_directory_files(tmp_path, follow_symlinks=True)
    assert [item.uri for item in files] == ["memory:///a.sysml"]

    monkeypatch.setattr(directory, "_inside", lambda root, resolved: False)
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, include="a.sysml")


def test_duplicate_generated_uri_defense(tmp_path, monkeypatch):
    write(tmp_path / "a.sysml", "package A {}")
    write(tmp_path / "b.sysml", "package B {}")
    monkeypatch.setattr(directory, "_memory_uri", lambda root, rel, relative: "memory:///same.sysml")
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path)


def test_symlink_directory_loop(tmp_path):
    write(tmp_path / "a.sysml", "package A {}")
    loop = tmp_path / "loop"
    loop.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(SysMLDirectoryError):
        collect_directory_files(tmp_path, follow_symlinks=True)


def test_private_helpers_cover_edge_cases():
    assert _glob_to_regex("**/*.sysml").match("a.sysml")
    assert _glob_to_regex("a?.sysml").match("ab.sysml")
    assert not _matcher((), ())(Path("a.sysml"))
    assert directory._inside("relative", "/absolute") is False
    assert _memory_uri(type("Root", (), {"name": ""})(), "a.sysml", False) == (
        "memory:///workspace/a.sysml"
    )
    with pytest.raises(SysMLDirectoryError):
        _memory_uri(type("Root", (), {"name": "r"})(), "../a.sysml", True)
    assert os.path.sep


def test_append_file_if_regular_helper():
    files = []
    regular = type("Regular", (), {"is_file": lambda self: True})()
    special = type("Special", (), {"is_file": lambda self: False})()

    assert _append_file_if_regular(files, "display", regular) is True
    assert files == [("display", regular)]
    assert _append_file_if_regular(files, "ignored", special) is False
    assert files == [("display", regular)]
