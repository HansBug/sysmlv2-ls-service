#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execFileSync } from "node:child_process";

const outputPath = "docs/generated/cli/index.md";
const commands = [
  { title: "Top-level help", args: ["--help"] },
  { title: "Version flag", args: ["--version"] },
  { title: "Health", args: ["health", "--help"] },
  { title: "Capabilities", args: ["capabilities", "--help"] },
  { title: "Version", args: ["version", "--help"] },
  { title: "Validate", args: ["validate", "--help"] },
  { title: "Validate text", args: ["validate", "text", "--help"] },
  { title: "Validate files", args: ["validate", "files", "--help"] },
  { title: "Validate directory", args: ["validate", "directory", "--help"] },
];

function runHelp(args) {
  try {
    return execFileSync("sysmlv2sl", args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    }).trimEnd();
  } catch (error) {
    const stderr = error.stderr?.toString() ?? "";
    throw new Error(
      `Unable to run sysmlv2sl ${args.join(" ")}. Install the Python client first: python -m pip install -e clients/python.\n${stderr}`,
      { cause: error },
    );
  }
}

const sections = commands.map((command) => {
  const invocation = `sysmlv2sl ${command.args.join(" ")}`;
  return `## ${command.title}\n\n\`\`\`console\n$ ${invocation}\n${runHelp(command.args)}\n\`\`\``;
});

const markdown = `# sysmlv2sl CLI reference\n\nThis page is generated from the installed \`sysmlv2sl\` Click command. Regenerate it with \`pnpm run docs:generate:cli\` after changing CLI behavior or help text.\n\n${sections.join("\n\n")}\n`;

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, markdown);
