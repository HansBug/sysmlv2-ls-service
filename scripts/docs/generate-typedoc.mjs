#!/usr/bin/env node
import { rmSync } from "node:fs";
import { execFileSync } from "node:child_process";

const outDir = "docs/generated/typedoc";
rmSync(outDir, { recursive: true, force: true });

execFileSync(
  "pnpm",
  [
    "exec",
    "typedoc",
    "--entryPoints",
    "src/app.ts",
    "src/contracts.ts",
    "src/diagnostics.ts",
    "src/limits.ts",
    "src/sysml-validator.ts",
    "src/uri.ts",
    "src/version.ts",
    "--out",
    outDir,
    "--plugin",
    "typedoc-plugin-markdown",
    "--readme",
    "none",
    "--hideBreadcrumbs",
    "--excludePrivate",
    "--excludeInternal",
    "--disableSources",
    "--skipErrorChecking",
  ],
  { stdio: "inherit" },
);
