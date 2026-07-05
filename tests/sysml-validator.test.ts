import { describe, expect, it } from "vitest";
import { validateSysML } from "../src/sysml-validator.js";

describe("validateSysML", () => {
  it("accepts a simple SysML package", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///ok.sysml",
          text: "package Demo { part def Vehicle; }",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
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
          text: "package Demo { part def }",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
    });

    expect(result.ok).toBe(false);
    expect(result.diagnostics.length).toBeGreaterThan(0);
    expect(result.diagnostics[0]).toMatchObject({
      severity: "error",
      uri: result.files[0]?.uri,
    });
  });

  it("marks syntax failures as not ok when validation checks are disabled", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///bad.sysml",
          text: "garbage!!!",
        },
      ],
      standardLibrary: "none",
      validationChecks: "none",
    });

    expect(result.ok).toBe(false);
    expect(result.files[0]?.parserErrors).toBeGreaterThan(0);
  });

  it("preserves caller URIs in file summaries and diagnostics", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///bad.sysml",
          text: "package Demo { part def }",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
    });

    expect(result.files[0]?.uri).toBe("memory:///bad.sysml");
    expect(result.diagnostics[0]?.uri).toBe("memory:///bad.sysml");
  });

  it("uses generated document URIs when callers omit uri and path", async () => {
    const result = await validateSysML({
      files: [
        {
          text: "package Generated {}",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
    });

    expect(result.ok).toBe(true);
    expect(result.files[0]?.uri).toBe("memory:/workspace/input-0.sysml");
  });

  it("resolves references across files in one request", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///lib.sysml",
          text: "package Lib { part def Base; }",
        },
        {
          uri: "memory:///use.sysml",
          text: "package Use { public import Lib::*; part base : Base; }",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
    });

    expect(result.ok).toBe(true);
    expect(result.diagnostics).toEqual([]);
  });

  it("accepts a simple KerML package", async () => {
    const result = await validateSysML({
      files: [
        {
          uri: "memory:///ok.kerml",
          text: "package KernelDemo { class Thing; }",
        },
      ],
      standardLibrary: "none",
      validationChecks: "all",
    });

    expect(result.ok).toBe(true);
    expect(result.diagnostics).toEqual([]);
    expect(result.files[0]?.language).toBe("kerml");
  });
});
