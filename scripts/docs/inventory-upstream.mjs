#!/usr/bin/env node
import {
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative } from "node:path";
import { execFileSync } from "node:child_process";

const upstreamRoot = "upstream/sysml-2ls";
const languageServerRoot = `${upstreamRoot}/packages/syside-languageserver`;
const validationRoot = `${languageServerRoot}/src/services/validation`;
const compiledValidationRoot = `${languageServerRoot}/lib/services/validation`;
const grammarRoot = `${languageServerRoot}/src/grammar`;
const requiredCompiledArtifacts = [
  `${compiledValidationRoot}/sysml-validator.js`,
  `${compiledValidationRoot}/kerml-validator.js`,
  `${languageServerRoot}/lib/generated/grammar.js`,
  `${languageServerRoot}/lib/generated/ast.d.ts`,
];

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

function walk(directory, predicate) {
  const entries = [];
  for (const name of readdirSync(directory)) {
    const path = join(directory, name);
    const stat = statSync(path);
    if (stat.isDirectory()) entries.push(...walk(path, predicate));
    else if (!predicate || predicate(path)) entries.push(path);
  }
  return entries.sort();
}

function ensureCompiledUpstream() {
  const missing = requiredCompiledArtifacts.filter((path) => {
    try {
      return !statSync(path).isFile();
    } catch (_error) {
      return true;
    }
  });
  if (missing.length > 0) {
    throw new Error(
      `Upstream build artifacts are missing. Run pnpm run build:upstream before inventory. Missing: ${missing.join(", ")}`,
    );
  }
}

function header(kind) {
  const upstreamPackage = readJson(`${languageServerRoot}/package.json`);
  return {
    schemaVersion: `upstream-${kind}-inventory/v1`,
    sourceKind: "static",
    analysisTarget: "typescript-source",
    analysisPolicy:
      "This first inventory version statically scans upstream TypeScript grammar and validator source. It verifies compiled JS/d.ts artifacts exist so the pinned submodule has been built, but those compiled artifacts are not primary parser evidence yet.",
    compiledArtifacts: {
      presenceChecked: true,
      primaryEvidence: false,
      requiredPaths: requiredCompiledArtifacts.map((path) =>
        relative(upstreamRoot, path),
      ),
    },
    serviceRepository: {
      repository: "https://github.com/HansBug/sysmlv2-ls-service",
      revision: "resolved-at-build-time",
      sourceDate: "resolved-at-build-time",
      metadataPolicy:
        "Committed inventory uses deterministic placeholders for the service repository; the MkDocs version hook resolves the rendered site revision/source date at build time.",
    },
    upstream: {
      repository: "https://github.com/sensmetry/sysml-2ls",
      revision: command(["git", "-C", upstreamRoot, "rev-parse", "HEAD"]),
      packageName: upstreamPackage.name ?? "syside-languageserver",
      packageVersion: upstreamPackage.version ?? "unknown",
    },
    toolchain: {
      requiredNodeVersion: "20.19",
      requiredPnpmVersion: "9.15.4",
      requiredPythonVersion: "3.12",
      runtimePolicy:
        "GitHub Actions docs job owns generation; Read the Docs consumes committed Markdown/JSON.",
    },
    generatedBy: "scripts/docs/inventory-upstream.mjs",
    generatedFor:
      "GitHub Actions docs job; Read the Docs consumes committed output only.",
  };
}

function decoratorsBefore(source, index, decoratorName) {
  const before = source.slice(0, index);
  const block = before.slice(Math.max(before.lastIndexOf("\n\n"), 0));
  const regex = new RegExp(`@${decoratorName}\\(([^)]*)\\)`, "g");
  const decorators = [];
  let match;
  while ((match = regex.exec(block)) !== null) decorators.push(match[1].trim());
  return decorators;
}

function semanticChecks() {
  const files = walk(validationRoot, (path) => path.endsWith("validator.ts"));
  const checks = [];
  for (const path of files) {
    const source = readFileSync(path, "utf8");
    const language = path.includes("sysml")
      ? "sysml"
      : path.includes("kerml")
        ? "kerml"
        : "shared";
    const methodPattern = /(?:async\s+)?(validate[A-Za-z0-9_]+)\s*\(/g;
    let match;
    while ((match = methodPattern.exec(source)) !== null) {
      const decorators = decoratorsBefore(
        source,
        match.index,
        language === "sysml" ? "validateSysML" : "validateKerML",
      );
      if (decorators.length === 0) continue;
      checks.push({
        id: `${language}:${match[1]}`,
        language,
        checkName: match[1],
        decorators,
        sourcePath: relative(upstreamRoot, path),
        sourceKind: "static",
        analysisTarget: "typescript-source",
        confidence: "medium",
      });
    }
  }
  return checks.sort((a, b) => a.id.localeCompare(b.id));
}

function diagnosticMessages(checks) {
  const records = [];
  for (const check of checks) {
    const path = join(upstreamRoot, check.sourcePath);
    const source = readFileSync(path, "utf8");
    const methodIndex = source.indexOf(check.checkName);
    const nextMethod = source
      .slice(methodIndex + check.checkName.length)
      .search(/\n\s*(?:async\s+)?validate[A-Za-z0-9_]+\s*\(/);
    const body =
      nextMethod === -1
        ? source.slice(methodIndex)
        : source.slice(
            methodIndex,
            methodIndex + check.checkName.length + nextMethod,
          );
    const literals = new Set();
    const patterns = [
      /accept\([^,]+,\s*[`'"]([^`'"]{8,240})[`'"]/g,
      /message:\s*[`'"]([^`'"]{8,240})[`'"]/g,
    ];
    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(body)) !== null)
        literals.add(match[1].replace(/\s+/g, " ").trim());
    }
    if (literals.size === 0) {
      records.push({
        id: `${check.id}:diagnostics-unspecified`,
        checkId: check.id,
        messagePattern:
          "No static message literal found by the inventory script.",
        sourceKind: "static",
        analysisTarget: check.analysisTarget,
        confidence: "low",
      });
    } else {
      Array.from(literals)
        .sort()
        .forEach((message, index) => {
          records.push({
            id: `${check.id}:diagnostic-${index + 1}`,
            checkId: check.id,
            messagePattern: message,
            sourceKind: "static",
            analysisTarget: check.analysisTarget,
            confidence: "medium",
          });
        });
    }
  }
  return records.sort((a, b) => a.id.localeCompare(b.id));
}

function grammarSurface() {
  const files = walk(grammarRoot, (path) => path.endsWith(".langium"));
  const records = [];
  for (const path of files) {
    const source = readFileSync(path, "utf8");
    const rel = relative(upstreamRoot, path);
    const rulePattern =
      /^(entry\s+)?([A-Z][A-Za-z0-9_]*)\s+(?:returns\s+([A-Za-z0-9_]+)\s*)?:/gm;
    let match;
    while ((match = rulePattern.exec(source)) !== null) {
      records.push({
        id: `${rel}:${match[2]}`,
        ruleName: match[2],
        entry: Boolean(match[1]),
        returns: match[3] ?? null,
        sourcePath: rel,
        sourceKind: "static",
        analysisTarget: "typescript-source",
        confidence: "medium",
      });
    }
    const typePattern = /^type\s+([A-Za-z0-9_]+)\s*=/gm;
    while ((match = typePattern.exec(source)) !== null) {
      records.push({
        id: `${rel}:type:${match[1]}`,
        ruleName: match[1],
        entry: false,
        returns: "type-alias",
        sourcePath: rel,
        sourceKind: "static",
        analysisTarget: "typescript-source",
        confidence: "medium",
      });
    }
  }
  return records.sort((a, b) => a.id.localeCompare(b.id));
}

function writeJson(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
}

function markdownCell(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\\/g, "\\\\")
    .replace(/\|/g, "\\|")
    .replace(/\r?\n/g, " ");
}

function table(rows, columns) {
  const head = `| ${columns.map((column) => column.title).join(" | ")} |`;
  const sep = `| ${columns.map(() => "---").join(" | ")} |`;
  const body = rows
    .map(
      (row) =>
        `| ${columns.map((column) => markdownCell(column.value(row))).join(" | ")} |`,
    )
    .join("\n");
  return `${head}\n${sep}\n${body}`;
}

function countBy(rows, key) {
  return rows.reduce((counts, row) => {
    const value = key(row);
    counts[value] = (counts[value] ?? 0) + 1;
    return counts;
  }, {});
}

function summaryTable(entries) {
  return table(
    entries.map(([metric, value]) => ({ metric, value })),
    [
      { title: "Metric", value: (row) => row.metric },
      { title: "Value", value: (row) => row.value },
    ],
  );
}

function compactSource(path) {
  return path.split("/").slice(-1)[0];
}

function compactDecorator(value) {
  return String(value)
    .replaceAll("ast.", "")
    .replace(/\s+/g, " ")
    .replace(/\[\s*/g, "excluding ")
    .replace(/\s*\]/g, "")
    .trim();
}

function writeMarkdown(path, title, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `# ${title}\n\n${content.trim()}\n`);
}

ensureCompiledUpstream();
const checks = semanticChecks();
const diagnostics = diagnosticMessages(checks);
const grammar = grammarSurface();
const semanticHeader = header("semantic-checks");
const diagnosticHeader = header("diagnostics");
const grammarHeader = header("grammar-surface");

writeJson("docs/_data/upstream/semantic-checks.json", {
  header: semanticHeader,
  checks,
});
writeJson("docs/_data/upstream/diagnostics.json", {
  header: diagnosticHeader,
  diagnostics,
});
writeJson("docs/_data/upstream/grammar-surface.json", {
  header: grammarHeader,
  grammar,
});

function inventoryIntro(description, currentHeader) {
  return `${description}\n\nInventory context: upstream package \`${currentHeader.upstream.packageVersion}\` at revision \`${currentHeader.upstream.revision}\`. Evidence target: TypeScript source. Compiled JS/d.ts artifacts are checked for presence after \`pnpm run build:upstream\`, but are not primary evidence in this first inventory version.`;
}

writeMarkdown(
  "docs/reference/upstream/semantic-checks.md",
  "Upstream semantic checks",
  `${inventoryIntro(
    "Generated inventory of validator methods discovered from the pinned upstream `sysml-2ls` submodule. These are structural SysML/KerML checks, not temporal model-checking results.",
    semanticHeader,
  )}

!!! warning "Static evidence"
    Rows are discovered from upstream TypeScript source. They show validator methods and decorators in the pinned submodule; they do not prove temporal model-checking capability or dynamic reachability from every service request.

## Summary

${summaryTable([
  ["Rows", checks.length],
  ["Unique check names", new Set(checks.map((row) => row.checkName)).size],
  [
    "Languages",
    Object.entries(countBy(checks, (row) => row.language))
      .map(([language, count]) => `\`${language}\`: ${count}`)
      .join(", "),
  ],
  [
    "Source files",
    Object.entries(countBy(checks, (row) => compactSource(row.sourcePath)))
      .map(([source, count]) => `\`${source}\`: ${count}`)
      .join(", "),
  ],
])}

## Complete discovered table

The table focuses on check names and decorators for readability. The summary lists compact source filenames, and the committed JSON data under \`docs/_data/upstream/semantic-checks.json\` retains full source paths and generator metadata.

<div class="compact-table wide-table" markdown>

${table(checks, [
  { title: "Check", value: (row) => `\`${row.checkName}\`` },
  { title: "Lang", value: (row) => row.language },
  {
    title: "Decorators",
    value: (row) =>
      row.decorators.map((item) => `\`${compactDecorator(item)}\``).join(", "),
  },
])}

</div>`,
);

writeMarkdown(
  "docs/reference/upstream/diagnostics-inventory.md",
  "Upstream diagnostics inventory",
  `${inventoryIntro(
    "Generated inventory of diagnostic message patterns statically associated with upstream validation checks. Low-confidence rows mean the script found a check but no direct message literal.",
    diagnosticHeader,
  )}

!!! warning "Message wording"
    Message patterns are static source evidence. Runtime diagnostics may include template interpolation or additional Langium/linking diagnostics that are not direct semantic-check literals.

## Summary

${summaryTable([
  ["Rows", diagnostics.length],
  [
    "Confidence",
    Object.entries(countBy(diagnostics, (row) => row.confidence))
      .map(([confidence, count]) => `\`${confidence}\`: ${count}`)
      .join(", "),
  ],
  ["Unique check IDs", new Set(diagnostics.map((row) => row.checkId)).size],
])}

## Complete discovered table

<div class="compact-table wide-table" markdown>

${table(diagnostics, [
  { title: "Check", value: (row) => `\`${row.checkId}\`` },
  {
    title: "Message pattern",
    value: (row) => row.messagePattern,
  },
  { title: "Confidence", value: (row) => row.confidence },
])}

</div>`,
);

writeMarkdown(
  "docs/reference/upstream/grammar-surface.md",
  "Upstream grammar surface",
  `${inventoryIntro(
    "Generated inventory of top-level Langium grammar rules and type aliases from the pinned upstream submodule. The generated parser may contain additional lower-level artifacts.",
    grammarHeader,
  )}

!!! info "Reading grammar rows"
    \`entry\` marks Langium entry rules. \`type-alias\` rows come from grammar interface files. This inventory is a surface map for documentation and investigation, not a replacement for the SysML/KerML specifications.

## Summary

${summaryTable([
  ["Rows", grammar.length],
  ["Entry rules", grammar.filter((row) => row.entry).length],
  [
    "Type aliases",
    grammar.filter((row) => row.returns === "type-alias").length,
  ],
  [
    "Source files",
    Object.entries(countBy(grammar, (row) => compactSource(row.sourcePath)))
      .map(([source, count]) => `\`${source}\`: ${count}`)
      .join(", "),
  ],
])}

## Complete discovered table

The table uses compact source filenames for readability. The committed JSON data under \`docs/_data/upstream/grammar-surface.json\` retains full paths.

<div class="compact-table wide-table" markdown>

${table(grammar, [
  { title: "Rule/type", value: (row) => `\`${row.ruleName}\`` },
  { title: "Entry", value: (row) => (row.entry ? "yes" : "no") },
  { title: "Returns", value: (row) => row.returns ?? "" },
  { title: "Source", value: (row) => `\`${compactSource(row.sourcePath)}\`` },
])}

</div>`,
);
