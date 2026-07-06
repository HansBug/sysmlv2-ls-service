#!/usr/bin/env node
/**
 * Lightweight documentation secret scan.
 *
 * This script intentionally keeps local and CI docs checks self-contained
 * instead of downloading an external scanner. It is a scoped first-pass guard
 * for documentation paths and complements, rather than replaces, GitHub secret
 * scanning or a future gitleaks gate when higher assurance is required.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const roots = [
  "docs",
  "openapi",
  ".readthedocs.yaml",
  "mkdocs.yml",
  "redocly.yaml",
  "scripts/docs",
];
const suspiciousPatterns = [
  { name: "GitHub token", pattern: /gh[pousr]_[A-Za-z0-9_]{20,}/g },
  { name: "AWS access key", pattern: /AKIA[0-9A-Z]{16}/g },
  {
    name: "private key",
    pattern: /-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----/g,
  },
  {
    name: "generic secret assignment",
    pattern:
      /(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*["'][^"'\s]{12,}["']/gi,
  },
];

function walk(path) {
  const stat = statSync(path);
  if (stat.isDirectory()) {
    return readdirSync(path).flatMap((entry) => walk(join(path, entry)));
  }
  return [path];
}

const files = roots
  .flatMap((root) => walk(root))
  .filter((path) => !path.endsWith(".pyc"));
const findings = [];
for (const file of files) {
  const text = readFileSync(file, "utf8");
  for (const pattern of suspiciousPatterns) {
    if (pattern.pattern.test(text))
      findings.push(`${file}: possible ${pattern.name}`);
    pattern.pattern.lastIndex = 0;
  }
}

if (findings.length > 0) {
  for (const finding of findings) console.error(finding);
  process.exit(1);
}
