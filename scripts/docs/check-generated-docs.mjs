#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const args = new Set(process.argv.slice(2));
const scope = args.has("--scope")
  ? process.argv[process.argv.indexOf("--scope") + 1]
  : args.has("--full")
    ? "full"
    : "base";

const basePaths = [
  "docs/_data/version.json",
  "docs/generated/cli/index.md",
  "docs/generated/openapi/index.md",
  "docs/generated/typedoc",
];
// These sentinel files keep generated trees from silently disappearing while
// avoiding a brittle full file manifest in this lightweight drift gate.
const requiredBaseFiles = [
  "docs/_data/version.json",
  "docs/generated/cli/index.md",
  "docs/generated/openapi/index.md",
  "docs/generated/typedoc/README.md",
  "docs/generated/typedoc/modules/app.md",
];
const fullPaths = [
  ...basePaths,
  "docs/_data/upstream/diagnostics.json",
  "docs/_data/upstream/semantic-checks.json",
  "docs/_data/upstream/grammar-surface.json",
  "docs/reference/upstream/diagnostics-inventory.md",
  "docs/reference/upstream/semantic-checks.md",
  "docs/reference/upstream/grammar-surface.md",
  "docs/reference/upstream/import-resolution.md",
  "docs/reference/upstream/limitations.md",
];
const paths = scope === "full" ? fullPaths : basePaths;
const requiredFiles =
  scope === "full"
    ? [
        ...requiredBaseFiles,
        "docs/_data/upstream/diagnostics.json",
        "docs/_data/upstream/semantic-checks.json",
        "docs/_data/upstream/grammar-surface.json",
        "docs/reference/upstream/diagnostics-inventory.md",
        "docs/reference/upstream/semantic-checks.md",
        "docs/reference/upstream/grammar-surface.md",
        "docs/reference/upstream/import-resolution.md",
        "docs/reference/upstream/limitations.md",
      ]
    : requiredBaseFiles;

function command(args) {
  return execFileSync(args[0], args.slice(1), {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

const missing = requiredFiles.filter((path) => !existsSync(path));
if (missing.length > 0) {
  console.error(`Generated docs are missing: ${missing.join(", ")}`);
  process.exit(1);
}

for (const path of requiredFiles) {
  try {
    execFileSync("git", ["ls-files", "--error-unmatch", "--", path], {
      stdio: "ignore",
    });
  } catch (_error) {
    console.error(`${path} must be committed generated documentation.`);
    process.exit(1);
  }
}

const version = readFileSync("VERSION", "utf8").trim();
const versionStamp = readJson("docs/_data/version.json");
if (versionStamp.service.version !== version) {
  console.error(
    `docs/_data/version.json service version ${versionStamp.service.version} does not match VERSION ${version}`,
  );
  process.exit(1);
}

if (versionStamp.repository.revision !== "resolved-at-build-time") {
  console.error(
    "docs/_data/version.json must keep repository.revision as resolved-at-build-time; the MkDocs hook resolves the actual commit during each build.",
  );
  process.exit(1);
}

if (versionStamp.repository.sourceDate !== "resolved-at-build-time") {
  console.error(
    "docs/_data/version.json must keep repository.sourceDate as resolved-at-build-time; the MkDocs hook resolves the actual source date during each build.",
  );
  process.exit(1);
}

if (!versionStamp.toolchain.requiredNodeVersion) {
  console.error("docs/_data/version.json must record requiredNodeVersion.");
  process.exit(1);
}

if (!versionStamp.toolchain.requiredPnpmVersion) {
  console.error("docs/_data/version.json must record requiredPnpmVersion.");
  process.exit(1);
}

if (scope === "full") {
  const upstreamRevision = command([
    "git",
    "-C",
    "upstream/sysml-2ls",
    "rev-parse",
    "HEAD",
  ]);
  const upstreamVersion = readJson(
    "upstream/sysml-2ls/packages/syside-languageserver/package.json",
  ).version;
  const upstreamDataFiles = [
    "docs/_data/upstream/diagnostics.json",
    "docs/_data/upstream/semantic-checks.json",
    "docs/_data/upstream/grammar-surface.json",
  ];
  for (const path of upstreamDataFiles) {
    const data = readJson(path);
    if (data.header.upstream.revision !== upstreamRevision) {
      console.error(
        `${path} has stale upstream revision ${data.header.upstream.revision}`,
      );
      process.exit(1);
    }
    if (data.header.upstream.packageVersion !== upstreamVersion) {
      console.error(
        `${path} has stale upstream package version ${data.header.upstream.packageVersion}`,
      );
      process.exit(1);
    }
    if (
      data.header.serviceRepository?.revision !== "resolved-at-build-time" ||
      data.header.serviceRepository?.sourceDate !== "resolved-at-build-time"
    ) {
      console.error(
        `${path} must record resolved-at-build-time service repository metadata placeholders.`,
      );
      process.exit(1);
    }
    if (!data.header.toolchain?.requiredNodeVersion) {
      console.error(`${path} must record requiredNodeVersion.`);
      process.exit(1);
    }
    if (!data.header.toolchain?.requiredPnpmVersion) {
      console.error(`${path} must record requiredPnpmVersion.`);
      process.exit(1);
    }
    if (data.header.analysisTarget !== "typescript-source") {
      console.error(
        `${path} analysisTarget must be typescript-source unless the inventory parser is upgraded to use compiled JS/d.ts as primary evidence.`,
      );
      process.exit(1);
    }
    if (data.header.compiledArtifacts?.presenceChecked !== true) {
      console.error(`${path} must record compiled artifact presence checks.`);
      process.exit(1);
    }
  }

  for (const path of [
    "docs/reference/upstream/import-resolution.md",
    "docs/reference/upstream/limitations.md",
  ]) {
    const text = readFileSync(path, "utf8");
    if (!text.includes(upstreamRevision) || !text.includes(upstreamVersion)) {
      console.error(
        `${path} must mention current upstream revision ${upstreamRevision} and package version ${upstreamVersion}.`,
      );
      process.exit(1);
    }
  }
}

try {
  const status = execFileSync(
    "git",
    ["status", "--porcelain", "--", ...paths],
    {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  if (status.trim().length > 0) {
    process.stdout.write(status);
    throw new Error("stale-or-untracked-docs");
  }
} catch (_error) {
  console.error(
    `Generated docs are stale or contain untracked files for scope ${scope}. Run pnpm run docs:generate:${scope} and commit the result.`,
  );
  process.exit(1);
}
