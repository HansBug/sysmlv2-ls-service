import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import type { VersionResponse } from "./contracts.js";

const require = createRequire(import.meta.url);

interface PackageInfo {
  name?: string;
  version?: string;
  repository?: string | { url?: string };
}

export function readPackageInfo(paths: string[]): PackageInfo {
  for (const path of paths) {
    try {
      return require(path) as PackageInfo;
    } catch {
      // Try the next candidate. Source runs use ../, built runtime falls back to ../../.
    }
  }
  return {};
}

export function readVersionFile(paths: string[]): string | undefined {
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

export function repositoryUrl(repository: PackageInfo["repository"], fallback: string): string {
  if (typeof repository === "string") return repository;
  return repository?.url ?? fallback;
}

export function envOverride(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value && value !== "unknown" ? value : undefined;
}

const servicePackage = readPackageInfo(["../package.json", "../../package.json"]);
const serviceVersionFile = readVersionFile(["../VERSION", "../../VERSION"]);
const upstreamPackage = readPackageInfo([
  "../upstream/sysml-2ls/packages/syside-languageserver/package.json",
  "../../upstream/sysml-2ls/packages/syside-languageserver/package.json"
]);

interface VersionInfoSources {
  servicePackage: PackageInfo;
  serviceVersionFile?: string;
  upstreamPackage: PackageInfo;
}

export function composeVersionInfo(sources: VersionInfoSources): VersionResponse {
  return {
    service: {
      name: sources.servicePackage.name ?? "sysmlv2-ls-service",
      version:
        envOverride("SERVICE_VERSION") ??
        sources.serviceVersionFile ??
        sources.servicePackage.version ??
        "0.0.0",
      revision: envOverride("SERVICE_REVISION") ?? "unknown",
      sourceRepository:
        envOverride("SOURCE_REPOSITORY") ??
        repositoryUrl(
          sources.servicePackage.repository,
          "https://github.com/HansBug/sysmlv2-ls-service"
        )
    },
    upstream: {
      sysml2ls: {
        version: envOverride("UPSTREAM_SYSML_2LS_VERSION") ?? sources.upstreamPackage.version ?? "unknown",
        revision: envOverride("UPSTREAM_SYSML_2LS_REVISION") ?? "unknown",
        packageName: sources.upstreamPackage.name ?? "syside-languageserver",
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

export function getVersionInfo(): VersionResponse {
  return composeVersionInfo({
    servicePackage,
    serviceVersionFile,
    upstreamPackage
  });
}
