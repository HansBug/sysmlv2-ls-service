#!/usr/bin/env python3
"""Check Python client public pydoc conventions."""

import ast
import re
import sys
from pathlib import Path


ROOT = Path("clients/python/src/sysmlv2slclient")
PRIVATE_MODULES = {"_version.py"}


def _public_name(name):
    return not name.startswith("_")


def _doc(node):
    return ast.get_docstring(node) or ""


def _has_restructured_param_docs(doc, args):
    missing = []
    for arg in args:
        if arg in ("self", "cls"):
            continue
        if ":param %s:" % arg not in doc:
            missing.append(":param %s:" % arg)
        if ":type %s:" % arg not in doc:
            missing.append(":type %s:" % arg)
    return missing


def _has_single_backtick_literal(doc):
    doc_without_roles = re.sub(r":[A-Za-z][A-Za-z0-9_-]*:`[^`]+`", "", doc)
    return re.search(r"(?<!`)`(?!`)", doc_without_roles) is not None


def _has_raise_statement(node):
    return any(isinstance(child, ast.Raise) for child in ast.walk(node))


def _check_doc(path, node, name, args=(), require_return=False, require_raises=False):
    doc = _doc(node)
    errors = []
    if not doc:
        return ["%s:%s missing docstring" % (path, name)]
    if "Example::" not in doc:
        errors.append("%s:%s docstring must include Example::" % (path, name))
    if _has_single_backtick_literal(doc):
        errors.append(
            "%s:%s docstring must use reST double-backtick literals" % (path, name)
        )
    errors.extend(
        "%s:%s missing %s" % (path, name, item)
        for item in _has_restructured_param_docs(doc, args)
    )
    if require_return:
        if ":return:" not in doc:
            errors.append("%s:%s missing :return:" % (path, name))
        if ":rtype:" not in doc:
            errors.append("%s:%s missing :rtype:" % (path, name))
    if require_raises and ":raises" not in doc:
        errors.append("%s:%s missing :raises: for public raise path" % (path, name))
    return errors


def _function_args(node):
    return [arg.arg for arg in node.args.args]


def _check_module(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    doc = _doc(tree)
    errors = []
    if not doc:
        errors.append("%s missing module docstring" % path)
    elif len(doc.splitlines()) < 3:
        errors.append("%s module docstring must explain purpose beyond one line" % path)
    if path.name == "__init__.py":
        required = ["Module roadmap", "Export", "Purpose"]
        for item in required:
            if item not in doc:
                errors.append("%s __init__ roadmap docstring missing %s" % (path, item))

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and _public_name(node.name):
            init_args = []
            init_node = None
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_args = _function_args(item)
                    init_node = item
                    break
            errors.extend(
                _check_doc(
                    path,
                    node,
                    node.name,
                    init_args,
                    require_raises=init_node is not None
                    and _has_raise_statement(init_node),
                )
            )
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and _public_name(item.name):
                    if item.name == "__init__":
                        continue
                    require_return = item.name not in ("raise_for_diagnostics",)
                    errors.extend(
                        _check_doc(
                            path,
                            item,
                            "%s.%s" % (node.name, item.name),
                            _function_args(item),
                            require_return,
                            _has_raise_statement(item),
                        )
                    )
        elif isinstance(node, ast.FunctionDef) and _public_name(node.name):
            returns = node.name not in ("cli",)
            errors.extend(
                _check_doc(
                    path,
                    node,
                    node.name,
                    _function_args(node),
                    returns,
                    _has_raise_statement(node),
                )
            )
    return errors


def main():
    errors = []
    for path in sorted(ROOT.glob("*.py")):
        if path.name in PRIVATE_MODULES:
            continue
        errors.extend(_check_module(path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
