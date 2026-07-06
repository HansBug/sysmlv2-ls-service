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
    responses: Object.keys(operation.responses ?? {}).join(", "),
  })),
);

const endpointTable = rows
  .map(
    (row) =>
      `| \`${row.method}\` | \`${row.path}\` | \`${row.operationId}\` | ${row.summary} | ${row.responses} |`,
  )
  .join("\n");

const schemas = Object.entries(spec.components.schemas)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([name, schema]) => {
    const required = Array.isArray(schema.required)
      ? schema.required.map((item) => `\`${item}\``).join(", ")
      : "";
    const propertyCount = schema.properties
      ? Object.keys(schema.properties).length
      : 0;
    return `| \`${name}\` | ${schema.type ?? "object"} | ${propertyCount} | ${required || "n/a"} |`;
  })
  .join("\n");

const markdown = `## Generated endpoint summary

Generated from \`${specPath}\`. Regenerate this section with \`pnpm run docs:generate:openapi\` after changing the OpenAPI document.

| Method | Path | Operation | Summary | Responses |
| --- | --- | --- | --- | --- |
${endpointTable}

## Generated schema index

| Schema | Type | Properties | Required fields |
| --- | --- | --- | --- |
${schemas}
`;

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, markdown);
