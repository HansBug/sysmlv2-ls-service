import { readFileSync } from "node:fs";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { FastifyInstance } from "fastify";
import { buildApp } from "../src/app.js";
import { DEFAULT_SERVICE_LIMITS, type ServiceLimits } from "../src/limits.js";
import { getVersionInfo } from "../src/version.js";

const serviceVersion = readFileSync(new URL("../VERSION", import.meta.url), "utf8").trim();
const upstreamVersion = JSON.parse(
  readFileSync(
    new URL(
      "../upstream/sysml-2ls/packages/syside-languageserver/package.json",
      import.meta.url
    ),
    "utf8"
  )
).version;

function limits(overrides: Partial<ServiceLimits> = {}): ServiceLimits {
  return {
    validate: {
      ...DEFAULT_SERVICE_LIMITS.validate,
      ...overrides.validate
    },
    http: {
      ...DEFAULT_SERVICE_LIMITS.http,
      ...overrides.http
    }
  };
}

function successfulValidation() {
  return {
    ok: true,
    diagnostics: [],
    files: [],
    meta: {
      standardLibrary: "none" as const,
      validationChecks: "all" as const,
      elapsedMs: 0
    }
  };
}

describe("HTTP API", () => {
  let app: FastifyInstance;

  beforeAll(async () => {
    app = await buildApp({ logger: false });
  });

  afterAll(async () => {
    await app.close();
  });

  it("exposes health", async () => {
    const response = await app.inject({ method: "GET", url: "/healthz" });
    const version = getVersionInfo();

    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({
      ok: true,
      service: "sysmlv2-ls-service",
      version: version.service.version
    });
  });

  it("exposes version metadata", async () => {
    const response = await app.inject({ method: "GET", url: "/v1/version" });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({
      service: {
        name: "sysmlv2-ls-service",
        version: serviceVersion,
        sourceRepository: "https://github.com/HansBug/sysmlv2-ls-service"
      },
      upstream: {
        sysml2ls: {
          version: upstreamVersion,
          packageName: "syside-languageserver",
          repository: "https://github.com/sensmetry/sysml-2ls"
        }
      }
    });
  });

  it("lets explicit version environment values override package fallbacks", () => {
    const previous = {
      serviceVersion: process.env.SERVICE_VERSION,
      upstreamVersion: process.env.UPSTREAM_SYSML_2LS_VERSION,
      buildDate: process.env.BUILD_DATE
    };

    process.env.SERVICE_VERSION = "9.9.9-test";
    process.env.UPSTREAM_SYSML_2LS_VERSION = "8.8.8-test";
    process.env.BUILD_DATE = "2026-07-03T00:00:00Z";

    try {
      expect(getVersionInfo()).toMatchObject({
        service: { version: "9.9.9-test" },
        upstream: { sysml2ls: { version: "8.8.8-test" } },
        build: { date: "2026-07-03T00:00:00Z" }
      });
    } finally {
      process.env.SERVICE_VERSION = previous.serviceVersion;
      process.env.UPSTREAM_SYSML_2LS_VERSION = previous.upstreamVersion;
      process.env.BUILD_DATE = previous.buildDate;
    }
  });

  it("ignores unknown version environment placeholders", () => {
    const previous = {
      serviceVersion: process.env.SERVICE_VERSION,
      upstreamVersion: process.env.UPSTREAM_SYSML_2LS_VERSION,
      buildDate: process.env.BUILD_DATE
    };

    process.env.SERVICE_VERSION = "unknown";
    process.env.UPSTREAM_SYSML_2LS_VERSION = "unknown";
    process.env.BUILD_DATE = "unknown";

    try {
      expect(getVersionInfo()).toMatchObject({
        service: { version: serviceVersion },
        upstream: { sysml2ls: { version: upstreamVersion } },
        build: { date: "unknown" }
      });
    } finally {
      process.env.SERVICE_VERSION = previous.serviceVersion;
      process.env.UPSTREAM_SYSML_2LS_VERSION = previous.upstreamVersion;
      process.env.BUILD_DATE = previous.buildDate;
    }
  });

  it("does not expose internal error messages to clients", async () => {
    const errorApp = await buildApp({ logger: false });
    errorApp.get("/test/internal-error", async () => {
      throw new Error("secret-token-abc123");
    });

    try {
      const response = await errorApp.inject({ method: "GET", url: "/test/internal-error" });

      expect(response.statusCode).toBe(500);
      expect(response.json()).toMatchObject({
        error: "internal_error",
        message: "Internal server error."
      });
      expect(response.body).not.toContain("secret-token-abc123");
    } finally {
      await errorApp.close();
    }
  });

  it("exposes capabilities", async () => {
    const response = await app.inject({ method: "GET", url: "/v1/capabilities" });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({
      languages: [
        { id: "sysml", extensions: [".sysml"] },
        { id: "kerml", extensions: [".kerml"] }
      ],
      validationChecks: ["all", "none"],
      standardLibrary: ["none"],
      limits: DEFAULT_SERVICE_LIMITS
    });
  });

  it("exposes injected effective limits in capabilities", async () => {
    const limitedApp = await buildApp({
      logger: false,
      limits: limits({
        validate: {
          maxFiles: 2,
          maxFileTextBytes: null,
          maxTotalTextBytes: 4096,
          validationTimeoutMs: null
        },
        http: {
          bodyLimitBytes: null
        }
      })
    });

    try {
      const response = await limitedApp.inject({ method: "GET", url: "/v1/capabilities" });

      expect(response.statusCode).toBe(200);
      expect(response.json()).toMatchObject({
        limits: {
          validate: {
            maxFiles: 2,
            maxFileTextBytes: null,
            maxTotalTextBytes: 4096,
            validationTimeoutMs: null
          },
          http: {
            bodyLimitBytes: null
          }
        }
      });
    } finally {
      await limitedApp.close();
    }
  });

  it("validates a request body and returns diagnostics", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      payload: {
        files: [{ uri: "memory:///demo.sysml", text: "package Demo { part def Vehicle; }" }]
      }
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({ ok: true, diagnostics: [] });
  });

  it("returns a service error when validation exceeds the request timeout", async () => {
    const timeoutApp = await buildApp({
      logger: false,
      limits: limits({ validate: { ...DEFAULT_SERVICE_LIMITS.validate, validationTimeoutMs: 5 } }),
      validate: () => new Promise(() => undefined)
    });

    try {
      const response = await timeoutApp.inject({
        method: "POST",
        url: "/v1/validate",
        payload: {
          files: [{ uri: "memory:///slow.sysml", text: "package Slow {}" }]
        }
      });

      expect(response.statusCode).toBe(503);
      expect(response.json()).toMatchObject({
        error: "validation_timeout",
        message: "Validation exceeded 5 ms."
      });
    } finally {
      await timeoutApp.close();
    }
  });

  it("skips the validation timeout wrapper when the timeout limit is disabled", async () => {
    const timeoutApp = await buildApp({
      logger: false,
      limits: limits({
        validate: { ...DEFAULT_SERVICE_LIMITS.validate, validationTimeoutMs: null }
      }),
      validate: async () => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return successfulValidation();
      }
    });

    try {
      const response = await timeoutApp.inject({
        method: "POST",
        url: "/v1/validate",
        payload: {
          files: [{ uri: "memory:///slow.sysml", text: "package Slow {}" }]
        }
      });

      expect(response.statusCode).toBe(200);
      expect(response.json()).toMatchObject({ ok: true });
    } finally {
      await timeoutApp.close();
    }
  });

  it("uses dynamic file count limits from the request schema", async () => {
    const limitedApp = await buildApp({
      logger: false,
      limits: limits({ validate: { ...DEFAULT_SERVICE_LIMITS.validate, maxFiles: 1 } }),
      validate: async () => successfulValidation()
    });

    try {
      const response = await limitedApp.inject({
        method: "POST",
        url: "/v1/validate",
        payload: {
          files: [
            { uri: "memory:///one.sysml", text: "package One {}" },
            { uri: "memory:///two.sysml", text: "package Two {}" }
          ]
        }
      });

      expect(response.statusCode).toBe(400);
      expect(response.json()).toMatchObject({ error: "bad_request" });
    } finally {
      await limitedApp.close();
    }
  });

  it("skips disabled service-owned text and body limits", async () => {
    const unboundedApp = await buildApp({
      logger: false,
      limits: limits({
        validate: {
          maxFiles: null,
          maxFileTextBytes: null,
          maxTotalTextBytes: null,
          validationTimeoutMs: null
        },
        http: { bodyLimitBytes: null }
      }),
      validate: async () => successfulValidation()
    });

    try {
      const response = await unboundedApp.inject({
        method: "POST",
        url: "/v1/validate",
        headers: { "content-type": "application/json" },
        payload: JSON.stringify({
          files: [{ uri: "memory:///large.sysml", text: "x".repeat(6 * 1024 * 1024) }]
        })
      });

      expect(response.statusCode).toBe(200);
      expect(response.json()).toMatchObject({ ok: true });
    } finally {
      await unboundedApp.close();
    }
  });

  it("fails app construction for invalid limit environment variables", async () => {
    const previous = process.env.VALIDATE_MAX_FILES;
    process.env.VALIDATE_MAX_FILES = "invalid";

    try {
      await expect(buildApp({ logger: false })).rejects.toThrow("VALIDATE_MAX_FILES");
    } finally {
      if (previous === undefined) {
        delete process.env.VALIDATE_MAX_FILES;
      } else {
        process.env.VALIDATE_MAX_FILES = previous;
      }
    }
  });

  it("rejects duplicate file URIs", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      payload: {
        files: [
          { uri: "memory:///same.sysml", text: "package A {}" },
          { uri: "memory:///same.sysml", text: "package B {}" }
        ]
      }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toMatchObject({ error: "bad_request" });
  });

  it("rejects canonically duplicate file URIs", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      payload: {
        files: [
          { uri: "memory:///same.sysml", text: "package A {}" },
          { uri: "memory:/same.sysml", text: "package B {}" }
        ]
      }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toMatchObject({ error: "bad_request" });
  });

  it("rejects malformed request bodies", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      payload: { files: [] }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toMatchObject({ error: "bad_request" });
  });

  it("maps invalid JSON to a client error", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      headers: { "content-type": "application/json" },
      payload: "not-json"
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toMatchObject({ error: "bad_request" });
  });

  it("maps oversized bodies to payload-too-large", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      headers: { "content-type": "application/json" },
      payload: JSON.stringify({ files: [{ text: "x".repeat(6 * 1024 * 1024) }] })
    });

    expect(response.statusCode).toBe(413);
    expect(response.json()).toMatchObject({ error: "payload_too_large" });
  });
});
