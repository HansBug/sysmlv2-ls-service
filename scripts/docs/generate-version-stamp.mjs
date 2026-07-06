#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execFileSync } from "node:child_process";

const outputPath = "docs/_data/version.json";

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function command(args, fallback = "unknown") {
  try {
    return execFileSync(args[0], args.slice(1), {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch (_error) {
    return fallback;
  }
}

const packageJson = readJson("package.json");
const upstreamPackage = readJson(
  "upstream/sysml-2ls/packages/syside-languageserver/package.json",
);
const version = readFileSync("VERSION", "utf8").trim();
const upstreamRevision = command([
  "git",
  "-C",
  "upstream/sysml-2ls",
  "rev-parse",
  "HEAD",
]);

const stamp = {
  schemaVersion: "docs-version-stamp/v1",
  service: {
    name: packageJson.name ?? "sysmlv2-ls-service",
    version,
    sourceRepository: "https://github.com/HansBug/sysmlv2-ls-service",
  },
  repository: {
    revision: "resolved-at-build-time",
    sourceDate: "resolved-at-build-time",
    metadataPolicy:
      "Committed docs keep deterministic placeholders; scripts/docs/mkdocs_hooks/version_stamp.py resolves the actual repository revision and source date when MkDocs builds the site.",
  },
  upstream: {
    sysml2ls: {
      packageName: upstreamPackage.name ?? "syside-languageserver",
      version: upstreamPackage.version ?? "unknown",
      revision: upstreamRevision,
      repository: "https://github.com/sensmetry/sysml-2ls",
    },
  },
  toolchain: {
    generatedBy: "scripts/docs/generate-version-stamp.mjs",
    authoritativeGenerator: "GitHub Actions docs job",
    requiredNodeVersion: "20.19",
    requiredPnpmVersion: "9.15.4",
    requiredPythonVersion: "3.12",
    runtimePolicy:
      "GitHub Actions generates Node-derived docs with the pinned toolchain; Read the Docs builds MkDocs from committed artifacts.",
    rtdBehavior: "Read the Docs consumes committed generated artifacts only.",
  },
};

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(stamp, null, 2)}\n`);
