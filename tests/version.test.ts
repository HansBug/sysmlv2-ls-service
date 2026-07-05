import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  composeVersionInfo,
  envOverride,
  readPackageInfo,
  readVersionFile,
  repositoryUrl,
} from "../src/version.js";

describe("version metadata helpers", () => {
  const previousEnv = new Map<string, string | undefined>();

  afterEach(() => {
    for (const [name, value] of previousEnv) {
      if (value === undefined) {
        delete process.env[name];
      } else {
        process.env[name] = value;
      }
    }
    previousEnv.clear();
  });

  function setEnv(name: string, value: string): void {
    if (!previousEnv.has(name)) {
      previousEnv.set(name, process.env[name]);
    }
    process.env[name] = value;
  }

  it("falls back across package and version file candidates", () => {
    const directory = mkdtempSync(join(tmpdir(), "sysmlv2-ls-version-"));
    const packagePath = join(directory, "package.json");
    const versionPath = join(directory, "VERSION");

    try {
      writeFileSync(
        packagePath,
        JSON.stringify({ name: "pkg", version: "1.2.3" }),
      );
      writeFileSync(versionPath, "4.5.6\n");

      expect(readPackageInfo(["./missing-package.json", packagePath])).toEqual({
        name: "pkg",
        version: "1.2.3",
      });
      expect(readPackageInfo(["./missing-package.json"])).toEqual({});
      expect(
        readVersionFile(["./missing-version", pathToFileURL(versionPath).href]),
      ).toBe("4.5.6");
      expect(readVersionFile(["./missing-version"])).toBeUndefined();
    } finally {
      rmSync(directory, { recursive: true, force: true });
    }
  });

  it("normalizes repository and environment override values", () => {
    expect(repositoryUrl("https://example.test/repo.git", "fallback")).toBe(
      "https://example.test/repo.git",
    );
    expect(
      repositoryUrl({ url: "https://example.test/object.git" }, "fallback"),
    ).toBe("https://example.test/object.git");
    expect(repositoryUrl({}, "fallback")).toBe("fallback");

    expect(envOverride("MISSING_TEST_ENV")).toBeUndefined();
    setEnv("VERSION_HELPER_TEST_ENV", " value ");
    expect(envOverride("VERSION_HELPER_TEST_ENV")).toBe("value");
    setEnv("VERSION_HELPER_UNKNOWN_ENV", "unknown");
    expect(envOverride("VERSION_HELPER_UNKNOWN_ENV")).toBeUndefined();
  });

  it("composes metadata from explicit sources and documented fallbacks", () => {
    expect(
      composeVersionInfo({
        servicePackage: {},
        upstreamPackage: {},
      }),
    ).toMatchObject({
      service: {
        name: "sysmlv2-ls-service",
        version: "0.0.0",
        revision: "unknown",
        sourceRepository: "https://github.com/HansBug/sysmlv2-ls-service",
      },
      upstream: {
        sysml2ls: {
          version: "unknown",
          revision: "unknown",
          packageName: "syside-languageserver",
          repository: "https://github.com/sensmetry/sysml-2ls",
        },
      },
    });

    setEnv("SERVICE_VERSION", "9.0.0");
    setEnv("SERVICE_REVISION", "service-rev");
    setEnv("SOURCE_REPOSITORY", "https://example.test/service");
    setEnv("UPSTREAM_SYSML_2LS_VERSION", "8.0.0");
    setEnv("UPSTREAM_SYSML_2LS_REVISION", "upstream-rev");
    setEnv("UPSTREAM_SYSML_2LS_REPOSITORY", "https://example.test/upstream");

    expect(
      composeVersionInfo({
        servicePackage: {
          name: "package-service-name",
          version: "1.0.0",
          repository: "https://example.test/package",
        },
        serviceVersionFile: "2.0.0",
        upstreamPackage: {
          name: "package-upstream-name",
          version: "3.0.0",
        },
      }),
    ).toMatchObject({
      service: {
        name: "package-service-name",
        version: "9.0.0",
        revision: "service-rev",
        sourceRepository: "https://example.test/service",
      },
      upstream: {
        sysml2ls: {
          version: "8.0.0",
          revision: "upstream-rev",
          packageName: "package-upstream-name",
          repository: "https://example.test/upstream",
        },
      },
    });
  });
});
