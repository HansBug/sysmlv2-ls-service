import { describe, expect, it } from "vitest";
import { validateSysML } from "../src/sysml-validator.js";

describe("validateSysML", () => {
  it("accepts a simple SysML package", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///ok.sysml",
          text: "package Demo { part def Vehicle; }"
        }
      ],
      standardLibrary: "none",
      validationChecks: "all"
    });

    expect(result.ok).toBe(true);
    expect(result.diagnostics).toEqual([]);
    expect(result.files[0]?.language).toBe("sysml");
  });

  it("returns structured diagnostics for invalid syntax", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///bad.sysml",
          text: "package Demo { part def }"
        }
      ],
      standardLibrary: "none",
      validationChecks: "all"
    });

    expect(result.ok).toBe(false);
    expect(result.diagnostics.length).toBeGreaterThan(0);
    expect(result.diagnostics[0]).toMatchObject({
      severity: "error",
      uri: result.files[0]?.uri
    });
  });

  it("accepts a simple KerML package", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///ok.kerml",
          text: "package KernelDemo { class Thing; }"
        }
      ],
      standardLibrary: "none",
      validationChecks: "all"
    });

    expect(result.ok).toBe(true);
    expect(result.diagnostics).toEqual([]);
    expect(result.files[0]?.language).toBe("kerml");
  });
});
