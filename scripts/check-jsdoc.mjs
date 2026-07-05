#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOTS = [
  { directory: "src", requireModuleDoc: true },
  { directory: "tests", requireModuleDoc: false },
  { directory: "scripts", requireModuleDoc: false },
];

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

function normalizeJSDoc(comment) {
  return comment
    .replace(/^\/\*\*/, "")
    .replace(/\*\/$/, "")
    .split(/\r?\n/)
    .map((line) => line.replace(/^\s*\*\s?/, "").trim())
    .join("\n")
    .trim();
}

function isMeaningfulJSDoc(comment) {
  return /[A-Za-z0-9]/.test(normalizeJSDoc(comment));
}

function leadingJSDoc(source) {
  const match = /^\/\*\*[\s\S]*?\*\//.exec(source.trimStart());
  return match ? match[0] : undefined;
}

function jsdocBefore(source, index) {
  const before = source.slice(0, index).trimEnd();
  const match = /\/\*\*[\s\S]*?\*\/$/.exec(before);
  return match ? match[0] : undefined;
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

function checkFile(path, requireModuleDoc) {
  const source = readFileSync(path, "utf8");
  const errors = [];
  const moduleDoc = leadingJSDoc(source);
  if (requireModuleDoc && !hasLeadingBlockComment(source)) {
    errors.push(`${path}: missing module-level JSDoc block`);
  } else if (requireModuleDoc && moduleDoc && !isMeaningfulJSDoc(moduleDoc)) {
    errors.push(`${path}: module-level JSDoc block is empty`);
  }
  for (const declaration of exportedDeclarations(source)) {
    const declarationDoc = jsdocBefore(source, declaration.index);
    if (!declarationDoc) {
      errors.push(`${path}: exported ${declaration.name} is missing JSDoc`);
    } else if (!isMeaningfulJSDoc(declarationDoc)) {
      errors.push(`${path}: exported ${declaration.name} has empty JSDoc`);
    }
  }
  return errors;
}

const errors = ROOTS.flatMap((root) =>
  walk(root.directory).map((file) => ({ file, root })),
).flatMap(({ file, root }) => checkFile(file, root.requireModuleDoc));

if (errors.length > 0) {
  for (const error of errors) {
    console.error(error);
  }
  process.exit(1);
}
