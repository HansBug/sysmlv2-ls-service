import { describe, expect, it } from "vitest";
import type { Diagnostic } from "vscode-languageserver";
import { normalizeDiagnostic } from "../src/diagnostics.js";

const range = {
  start: { line: 0, character: 0 },
  end: { line: 0, character: 1 },
};

describe("normalizeDiagnostic", () => {
  it("preserves structured severity, source, and code fields", () => {
    expect(
      normalizeDiagnostic(
        {
          severity: 3,
          source: "custom",
          code: 7,
          message: "info",
          range,
        } satisfies Diagnostic,
        "memory:///info.sysml",
      ),
    ).toMatchObject({
      severity: "information",
      source: "custom",
      code: 7,
      uri: "memory:///info.sysml",
    });

    expect(
      normalizeDiagnostic(
        {
          severity: 4,
          message: "hint",
          range,
        } satisfies Diagnostic,
        "memory:///hint.sysml",
        "fallback",
      ),
    ).toMatchObject({
      severity: "hint",
      source: "fallback",
    });
  });

  it("defaults missing or unknown severity to error", () => {
    expect(
      normalizeDiagnostic(
        {
          message: "missing",
          range,
        } satisfies Diagnostic,
        "memory:///missing.sysml",
      ).severity,
    ).toBe("error");

    expect(
      normalizeDiagnostic(
        {
          severity: 99,
          message: "unknown",
          range,
        } as unknown as Diagnostic,
        "memory:///unknown.sysml",
      ).severity,
    ).toBe("error");
  });
});
