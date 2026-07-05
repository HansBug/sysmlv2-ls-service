/**
 * Version metadata composition.
 *
 * This module reads service package metadata, the canonical VERSION file,
 * upstream sysml-2ls package metadata, and build-time environment overrides to
 * assemble the public `/v1/version` response.
 *
 * @example
 * ```ts
 * const version = getVersionInfo();
 * ```
 */
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import type { VersionResponse } from "./contracts.js";

const require = createRequire(import.meta.url);

/**
 * Minimal package metadata consumed by the version metadata composer.
 */
export interface PackageInfo {
  /** Package name. */
  name?: string;
  /** Package version. */
  version?: string;
  /** Repository metadata as a URL string or package-json object. */
  repository?: string | { url?: string };
}

/**
 * Read package metadata from the first available package path.
 *
 * @param paths - Candidate paths relative to this module.
 * @returns Parsed package metadata or an empty object.
 *
 * @example
 * ```ts
 * readPackageInfo(["../package.json"]).version;
 * ```
 */
export function readPackageInfo(paths: string[]): PackageInfo {
  for (const path of paths) {
    try {
      return require(path) as PackageInfo;
    } catch (_error) {
      // Try the next candidate. Source runs use ../, built runtime falls back to ../../.
    }
  }
  return {};
}

/**
 * Read the canonical service version file from the first available path.
 *
 * @param paths - Candidate VERSION paths relative to this module.
 * @returns Trimmed version string, or `undefined` when no candidate exists.
 *
 * @example
 * ```ts
 * readVersionFile(["../VERSION"]);
 * ```
 */
export function readVersionFile(paths: string[]): string | undefined {
  for (const path of paths) {
    try {
      const version = readFileSync(
        new URL(path, import.meta.url),
        "utf8",
      ).trim();
      if (version) return version;
    } catch (_error) {
      // Try the next candidate. Source runs use ../, built runtime falls back to ../../.
    }
  }
  return undefined;
}

/**
 * Resolve a package repository value into a URL string.
 *
 * @param repository - Package repository field.
 * @param fallback - URL returned when repository metadata is missing.
 * @returns Repository URL.
 *
 * @example
 * ```ts
 * repositoryUrl({ url: "https://example.test/repo" }, "fallback");
 * ```
 */
export function repositoryUrl(
  repository: PackageInfo["repository"],
  fallback: string,
): string {
  if (typeof repository === "string") return repository;
  return repository?.url ?? fallback;
}

/**
 * Read a meaningful build metadata environment override.
 *
 * @param name - Environment variable name.
 * @returns Trimmed override value, or `undefined` for missing/placeholder
 * values.
 *
 * @example
 * ```ts
 * envOverride("SERVICE_VERSION");
 * ```
 */
export function envOverride(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value && value !== "unknown" ? value : undefined;
}

const servicePackage = readPackageInfo([
  "../package.json",
  "../../package.json",
]);
const serviceVersionFile = readVersionFile(["../VERSION", "../../VERSION"]);
const upstreamPackage = readPackageInfo([
  "../upstream/sysml-2ls/packages/syside-languageserver/package.json",
  "../../upstream/sysml-2ls/packages/syside-languageserver/package.json",
]);

/**
 * Explicit source inputs used to compose public version metadata.
 */
export interface VersionInfoSources {
  /** Service package metadata. */
  servicePackage: PackageInfo;
  /** Canonical VERSION file contents when available. */
  serviceVersionFile?: string;
  /** Upstream sysml-2ls package metadata. */
  upstreamPackage: PackageInfo;
}

/**
 * Compose version metadata from explicit source objects.
 *
 * @param sources - Package and VERSION metadata inputs.
 * @returns Public version response DTO.
 *
 * @example
 * ```ts
 * composeVersionInfo({
 *   servicePackage: { name: "svc", version: "1" },
 *   upstreamPackage: { name: "up", version: "2" }
 * });
 * ```
 */
export function composeVersionInfo(
  sources: VersionInfoSources,
): VersionResponse {
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
          "https://github.com/HansBug/sysmlv2-ls-service",
        ),
    },
    upstream: {
      sysml2ls: {
        version:
          envOverride("UPSTREAM_SYSML_2LS_VERSION") ??
          sources.upstreamPackage.version ??
          "unknown",
        revision: envOverride("UPSTREAM_SYSML_2LS_REVISION") ?? "unknown",
        packageName: sources.upstreamPackage.name ?? "syside-languageserver",
        repository:
          envOverride("UPSTREAM_SYSML_2LS_REPOSITORY") ??
          "https://github.com/sensmetry/sysml-2ls",
      },
    },
    build: {
      date: envOverride("BUILD_DATE") ?? "unknown",
      nodeVersion: process.version,
    },
  };
}

/**
 * Return version metadata for the current runtime.
 *
 * @returns Public version response DTO.
 *
 * @example
 * ```ts
 * getVersionInfo().service.name;
 * ```
 */
export function getVersionInfo(): VersionResponse {
  return composeVersionInfo({
    servicePackage,
    serviceVersionFile,
    upstreamPackage,
  });
}
