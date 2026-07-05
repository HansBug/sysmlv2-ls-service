#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOTS = ["src"];

function walk(directory) {
  const files = [];
  for (const entry of readdirSync(directory)) {
    const path = join(directory, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      files.push(...walk(path));
    } else if (/\.(ts|mts|cts|js|mjs)$/.test(path) && !path.endsWith(".d.ts")) {
      files.push(path);
    }
  }
  return files;
}

function hasLeadingBlockComment(source) {
  return source.trimStart().startsWith("/**");
}

function hasJSDocBefore(source, index) {
  const before = source.slice(0, index).trimEnd();
  return /\/\*\*[\s\S]*?\*\/$/.test(before);
}

function exportedDeclarations(source) {
  const pattern =
    /(^|\n)export\s+(?:async\s+)?(?:function|class|interface|type|const|let|var)\s+([A-Za-z0-9_]+)/g;
  const declarations = [];
  let match;
  while ((match = pattern.exec(source)) !== null) {
    declarations.push({ name: match[2], index: match.index + match[1].length });
  }
  return declarations;
}

function checkFile(path) {
  const source = readFileSync(path, "utf8");
  const errors = [];
  if (!hasLeadingBlockComment(source)) {
    errors.push(`${path}: missing module-level JSDoc block`);
  }
  for (const declaration of exportedDeclarations(source)) {
    if (!hasJSDocBefore(source, declaration.index)) {
      errors.push(`${path}: exported ${declaration.name} is missing JSDoc`);
    }
  }
  return errors;
}

const errors = ROOTS.flatMap((root) => walk(root)).flatMap((file) =>
  checkFile(file),
);

if (errors.length > 0) {
  for (const error of errors) {
    console.error(error);
  }
  process.exit(1);
}
