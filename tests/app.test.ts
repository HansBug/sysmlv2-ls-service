import { afterAll, beforeAll, describe, expect, it } from "vitest";
import type { FastifyInstance } from "fastify";
import { buildApp } from "../src/app.js";

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
    expect(response.statusCode).toBe(200);
    expect(response.json()).toMatchObject({ ok: true, service: "sysmlv2-ls-service" });
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
