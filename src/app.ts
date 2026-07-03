import Fastify, { type FastifyInstance } from "fastify";
import cors from "@fastify/cors";
import { ZodError } from "zod";
import {
  type CapabilitiesResponse,
  type HealthResponse,
  validateRequestSchema
} from "./contracts.js";
import { validateSysML } from "./sysml-validator.js";
import { makeDocumentUriKey } from "./uri.js";

export interface AppOptions {
  logger?: boolean;
}

function getErrorStatusCode(error: unknown): number {
  if (
    typeof error === "object" &&
    error !== null &&
    "statusCode" in error &&
    typeof error.statusCode === "number" &&
    error.statusCode >= 400
  ) {
    return error.statusCode;
  }
  return 500;
}

function rejectDuplicateDocumentUris(payload: ReturnType<typeof validateRequestSchema.parse>): void {
  const seenUris = new Set<string>();
  payload.files.forEach((file, index) => {
    const documentUri = makeDocumentUriKey(file, index);
    if (seenUris.has(documentUri)) {
      throw new ZodError([
        {
          code: "custom",
          path: ["files", index, "uri"],
          message: `Duplicate canonical file URI: ${documentUri}`
        }
      ]);
    }
    seenUris.add(documentUri);
  });
}

export async function buildApp(options: AppOptions = {}): Promise<FastifyInstance> {
  const app = Fastify({
    logger: options.logger ?? true,
    bodyLimit: 5 * 1024 * 1024
  });

  await app.register(cors, {
    origin: false
  });

  app.setErrorHandler((error, _request, reply) => {
    const statusCode = getErrorStatusCode(error);

    if (error instanceof ZodError) {
      reply.status(400).send({
        error: "bad_request",
        message: "Request body failed schema validation.",
        issues: error.issues
      });
      return;
    }

    if (statusCode >= 500) {
      app.log.error(error);
    } else {
      app.log.warn(error);
    }

    const message = error instanceof Error ? error.message : "Unknown error";
    reply.status(statusCode).send({
      error:
        statusCode === 413
          ? "payload_too_large"
          : statusCode < 500
            ? "bad_request"
            : "internal_error",
      message
    });
  });

  app.get("/healthz", async (): Promise<HealthResponse> => ({
    ok: true,
    service: "sysmlv2-ls-service",
    version: "0.1.0"
  }));

  app.get("/v1/capabilities", async (): Promise<CapabilitiesResponse> => ({
    languages: [
      { id: "sysml", extensions: [".sysml"] },
      { id: "kerml", extensions: [".kerml"] }
    ],
    validationChecks: ["all", "none"],
    standardLibrary: ["none"]
  }));

  app.post("/v1/validate", async (request) => {
    const payload = validateRequestSchema.parse(request.body);
    rejectDuplicateDocumentUris(payload);
    return validateSysML(payload);
  });

  return app;
}
