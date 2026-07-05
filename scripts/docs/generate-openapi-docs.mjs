#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import YAML from "yaml";

const specPath = "openapi/service.v1.yaml";
const outputPath = "docs/generated/openapi/index.md";
const spec = YAML.parse(readFileSync(specPath, "utf8"));

const rows = Object.entries(spec.paths).flatMap(([path, operations]) =>
  Object.entries(operations).map(([method, operation]) => ({
    method: method.toUpperCase(),
    path,
    operationId: operation.operationId ?? "",
    summary: operation.summary ?? "",
  })),
);

const endpointTable = rows
  .map(
    (row) =>
      `| \`${row.method}\` | \`${row.path}\` | \`${row.operationId}\` | ${row.summary} |`,
  )
  .join("\n");

const schemas = Object.keys(spec.components.schemas)
  .sort()
  .map((name) => `- \`${name}\``)
  .join("\n");

const markdown = `# OpenAPI reference\n\nThe canonical OpenAPI document is \`${specPath}\`. This generated page summarizes the service-owned HTTP contract; run \`pnpm run openapi:check\` to lint the spec and detect drift against the implementation.\n\n## Endpoints\n\n| Method | Path | Operation | Summary |\n| --- | --- | --- | --- |\n${endpointTable}\n\n## Schemas\n\n${schemas}\n`;

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, markdown);
