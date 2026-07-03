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

  it("rejects malformed request bodies", async () => {
    const response = await app.inject({
      method: "POST",
      url: "/v1/validate",
      payload: { files: [] }
    });

    expect(response.statusCode).toBe(400);
    expect(response.json()).toMatchObject({ error: "bad_request" });
  });
});
