import { describe, expect, it } from "vitest";
import { makeValidateRequestSchema } from "../src/contracts.js";
import { DEFAULT_SERVICE_LIMITS, type ServiceLimits } from "../src/limits.js";

function limits(overrides: Partial<ServiceLimits> = {}): ServiceLimits {
  return {
    validate: {
      ...DEFAULT_SERVICE_LIMITS.validate,
      ...overrides.validate,
    },
    http: {
      ...DEFAULT_SERVICE_LIMITS.http,
      ...overrides.http,
    },
  };
}

describe("validate request schema", () => {
  it("reports per-file and total UTF-8 byte limit failures", () => {
    const schema = makeValidateRequestSchema(
      limits({
        validate: {
          ...DEFAULT_SERVICE_LIMITS.validate,
          maxFileTextBytes: 3,
          maxTotalTextBytes: 5,
        },
      }),
    );

    const result = schema.safeParse({
      files: [
        { uri: "memory:///one.sysml", text: "1234" },
        { uri: "memory:///two.sysml", text: "é" },
      ],
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues.map((issue) => issue.path.join("."))).toEqual([
        "files.0.text",
        "files",
      ]);
    }
  });

  it("accepts files without explicit document ids and detects duplicate paths", () => {
    const schema = makeValidateRequestSchema(DEFAULT_SERVICE_LIMITS);

    expect(
      schema.parse({ files: [{ text: "package Anonymous {}" }] }),
    ).toMatchObject({
      standardLibrary: "none",
      validationChecks: "all",
    });

    const result = schema.safeParse({
      files: [
        { path: "/tmp/same.sysml", text: "package A {}" },
        { path: "/tmp/same.sysml", text: "package B {}" },
      ],
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toContain(
        "Duplicate file URI/path",
      );
    }
  });
});
