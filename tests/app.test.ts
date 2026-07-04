import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { FastifyInstance } from "fastify";
import { buildApp } from "../src/app.js";
import { getVersionInfo } from "../src/version.js";

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
        version: "0.1.0",
        sourceRepository: "https://github.com/HansBug/sysmlv2-ls-service"
      },
      upstream: {
        sysml2ls: {
          version: "0.9.1",
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
        service: { version: "0.1.0" },
        upstream: { sysml2ls: { version: "0.9.1" } },
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
      standardLibrary: ["none"]
    });
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
      validationTimeoutMs: 5,
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
