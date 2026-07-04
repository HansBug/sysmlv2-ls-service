import { describe, expect, it } from "vitest";
import {
  DEFAULT_HTTP_BODY_LIMIT_BYTES,
  DEFAULT_MAX_FILES,
  DEFAULT_MAX_FILE_TEXT_BYTES,
  DEFAULT_MAX_TOTAL_TEXT_BYTES,
  DEFAULT_VALIDATION_TIMEOUT_MS,
  resolveServiceLimits
} from "../src/limits.js";

describe("service limits", () => {
  it("uses documented defaults when environment variables are unset", () => {
    expect(resolveServiceLimits({})).toEqual({
      validate: {
        maxFiles: DEFAULT_MAX_FILES,
        maxFileTextBytes: DEFAULT_MAX_FILE_TEXT_BYTES,
        maxTotalTextBytes: DEFAULT_MAX_TOTAL_TEXT_BYTES,
        validationTimeoutMs: DEFAULT_VALIDATION_TIMEOUT_MS
      },
      http: {
        bodyLimitBytes: DEFAULT_HTTP_BODY_LIMIT_BYTES
      }
    });
  });

  it("reads positive integer overrides from the environment", () => {
    expect(
      resolveServiceLimits({
        VALIDATE_MAX_FILES: "2",
        VALIDATE_MAX_FILE_TEXT_BYTES: "3",
        VALIDATE_MAX_TOTAL_TEXT_BYTES: "4",
        HTTP_BODY_LIMIT_BYTES: "5",
        VALIDATION_TIMEOUT_MS: "6"
      })
    ).toEqual({
      validate: {
        maxFiles: 2,
        maxFileTextBytes: 3,
        maxTotalTextBytes: 4,
        validationTimeoutMs: 6
      },
      http: {
        bodyLimitBytes: 5
      }
    });
  });

  it("maps supported disabled values to null", () => {
    expect(
      resolveServiceLimits({
        VALIDATE_MAX_FILES: "0",
        VALIDATE_MAX_FILE_TEXT_BYTES: "none",
        VALIDATE_MAX_TOTAL_TEXT_BYTES: "unlimited",
        HTTP_BODY_LIMIT_BYTES: "NONE",
        VALIDATION_TIMEOUT_MS: "UNLIMITED"
      })
    ).toEqual({
      validate: {
        maxFiles: null,
        maxFileTextBytes: null,
        maxTotalTextBytes: null,
        validationTimeoutMs: null
      },
      http: {
        bodyLimitBytes: null
      }
    });
  });

  it("rejects invalid values instead of silently using defaults", () => {
    for (const [name, value] of [
      ["VALIDATE_MAX_FILES", "-1"],
      ["VALIDATE_MAX_FILE_TEXT_BYTES", "1.5"],
      ["VALIDATE_MAX_TOTAL_TEXT_BYTES", "abc"],
      ["HTTP_BODY_LIMIT_BYTES", ""],
      ["VALIDATION_TIMEOUT_MS", "NaN"]
    ]) {
      expect(() => resolveServiceLimits({ [name]: value })).toThrow(name);
    }
  });
});
