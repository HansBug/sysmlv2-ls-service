import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import type { VersionResponse } from "./contracts.js";

const require = createRequire(import.meta.url);

interface PackageInfo {
  name?: string;
  version?: string;
  repository?: string | { url?: string };
}

function readPackageInfo(paths: string[]): PackageInfo {
  for (const path of paths) {
    try {
      return require(path) as PackageInfo;
    } catch {
      // Try the next candidate. Source runs use ../, built runtime falls back to ../../.
    }
  }
  return {};
}

function readVersionFile(paths: string[]): string | undefined {
  for (const path of paths) {
    try {
      const version = readFileSync(new URL(path, import.meta.url), "utf8").trim();
      if (version) return version;
    } catch {
      // Try the next candidate. Source runs use ../, built runtime falls back to ../../.
    }
  }
  return undefined;
}

function repositoryUrl(repository: PackageInfo["repository"], fallback: string): string {
  if (typeof repository === "string") return repository;
  return repository?.url ?? fallback;
}

function envOverride(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value && value !== "unknown" ? value : undefined;
}

const servicePackage = readPackageInfo(["../package.json", "../../package.json"]);
const serviceVersionFile = readVersionFile(["../VERSION", "../../VERSION"]);
const upstreamPackage = readPackageInfo([
  "../upstream/sysml-2ls/packages/syside-languageserver/package.json",
  "../../upstream/sysml-2ls/packages/syside-languageserver/package.json"
]);

export function getVersionInfo(): VersionResponse {
  return {
    service: {
      name: servicePackage.name ?? "sysmlv2-ls-service",
      version: envOverride("SERVICE_VERSION") ?? serviceVersionFile ?? servicePackage.version ?? "0.0.0",
      revision: envOverride("SERVICE_REVISION") ?? "unknown",
      sourceRepository:
        envOverride("SOURCE_REPOSITORY") ??
        repositoryUrl(servicePackage.repository, "https://github.com/HansBug/sysmlv2-ls-service")
    },
    upstream: {
      sysml2ls: {
        version: envOverride("UPSTREAM_SYSML_2LS_VERSION") ?? upstreamPackage.version ?? "unknown",
        revision: envOverride("UPSTREAM_SYSML_2LS_REVISION") ?? "unknown",
        packageName: upstreamPackage.name ?? "syside-languageserver",
        repository:
          envOverride("UPSTREAM_SYSML_2LS_REPOSITORY") ??
          "https://github.com/sensmetry/sysml-2ls"
      }
    },
    build: {
      date: envOverride("BUILD_DATE") ?? "unknown",
      nodeVersion: process.version
    }
  };
}
