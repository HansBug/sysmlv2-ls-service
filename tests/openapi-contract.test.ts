import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import YAML from "yaml";
import { Ajv2020 } from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { buildApp } from "../src/app.js";
import type { ValidateResponse } from "../src/contracts.js";

const openapi = YAML.parse(readFileSync("openapi/service.v1.yaml", "utf8"));

function ajvForOpenApi() {
  const ajv = new Ajv2020({ strict: false, allErrors: true });
  (addFormats as unknown as (target: Ajv2020) => void)(ajv);
  for (const [name, schema] of Object.entries(openapi.components.schemas)) {
    ajv.addSchema(
      schema as Record<string, unknown>,
      `#/components/schemas/${name}`,
    );
  }
  return ajv;
}

function responseSchema(path: string, method: string, status = "200") {
  return openapi.paths[path][method].responses[status].content[
    "application/json"
  ].schema;
}

function documentedRouteKeys(): string[] {
  return Object.entries(openapi.paths)
    .flatMap(([path, methods]) =>
      Object.keys(methods as Record<string, unknown>).map(
        (method) => `${method.toUpperCase()} ${path}`,
      ),
    )
    .sort();
}

async function implementedPublicRouteKeys(): Promise<string[]> {
  const app = await buildApp({ logger: false });
  try {
    await app.ready();
    return app
      .printRoutes({ commonPrefix: false })
      .split("\n")
      .flatMap((line) => {
        const match = line.match(
          /^[├└]── (?<path>\/\S+|\*) \((?<methods>[^)]+)\)$/u,
        );
        if (!match?.groups || match.groups.path === "*") return [];
        return match.groups.methods
          .split(",")
          .map((method) => method.trim())
          .filter((method) => method !== "HEAD" && method !== "OPTIONS")
          .map((method) => `${method} ${match.groups?.path}`);
      })
      .sort();
  } finally {
    await app.close();
  }
}

describe("OpenAPI contract drift gate", () => {
  it("documents exactly the implemented public Fastify route surface", async () => {
    expect(await implementedPublicRouteKeys()).toEqual(documentedRouteKeys());
  });

  it("documents validate request enums and required file text", () => {
    const requestSchema = openapi.components.schemas.ValidateRequest;
    expect(requestSchema.required).toEqual(["files"]);
    expect(requestSchema.properties.standardLibrary.enum).toEqual(["none"]);
    expect(requestSchema.properties.validationChecks.enum).toEqual([
      "all",
      "none",
    ]);
    expect(openapi.components.schemas.SysMLFileInput.required).toEqual([
      "text",
    ]);
    expect(
      openapi.components.schemas.SysMLFileInput.properties.language.enum,
    ).toEqual(["sysml", "kerml"]);
  });

  it("validates actual success responses against documented schemas", async () => {
    const validateResponse: ValidateResponse = {
      ok: true,
      diagnostics: [],
      files: [
        {
          uri: "memory:///demo.sysml",
          language: "sysml",
          parserErrors: 0,
          lexerErrors: 0,
          diagnostics: 0,
        },
      ],
      meta: {
        standardLibrary: "none",
        validationChecks: "all",
        elapsedMs: 1,
      },
    };
    const app = await buildApp({
      logger: false,
      validate: async () => validateResponse,
    });
    const ajv = ajvForOpenApi();

    try {
      for (const route of [
        { path: "/healthz", openapiMethod: "get" },
        { path: "/v1/capabilities", openapiMethod: "get" },
        { path: "/v1/version", openapiMethod: "get" },
      ] as const) {
        const response = await app.inject({
          method: "GET",
          url: route.path,
        });
        const validate = ajv.compile(
          responseSchema(route.path, route.openapiMethod),
        );
        expect(validate(response.json()), JSON.stringify(validate.errors)).toBe(
          true,
        );
      }

      const response = await app.inject({
        method: "POST",
        url: "/v1/validate",
        payload: {
          files: [{ uri: "memory:///demo.sysml", text: "package Demo {}" }],
        },
      });
      const validate = ajv.compile(responseSchema("/v1/validate", "post"));
      expect(validate(response.json()), JSON.stringify(validate.errors)).toBe(
        true,
      );
    } finally {
      await app.close();
    }
  });

  it("validates actual service error shape against documented schema", async () => {
    const app = await buildApp({ logger: false });
    const ajv = ajvForOpenApi();
    try {
      const response = await app.inject({
        method: "POST",
        url: "/v1/validate",
        payload: {},
      });
      expect(response.statusCode).toBe(400);
      const validate = ajv.compile(
        responseSchema("/v1/validate", "post", "400"),
      );
      expect(validate(response.json()), JSON.stringify(validate.errors)).toBe(
        true,
      );
    } finally {
      await app.close();
    }
  });
});
