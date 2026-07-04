import Fastify, { type FastifyInstance } from "fastify";
import cors from "@fastify/cors";
import { ZodError } from "zod";
import {
  type CapabilitiesResponse,
  type HealthResponse,
  type ValidateRequest,
  type ValidateResponse,
  type VersionResponse,
  validateRequestSchema
} from "./contracts.js";
import { validateSysML } from "./sysml-validator.js";
import { makeDocumentUriKey } from "./uri.js";
import { getVersionInfo } from "./version.js";

const DEFAULT_VALIDATION_TIMEOUT_MS = 30_000;

type ValidateFunction = (request: ValidateRequest) => Promise<ValidateResponse>;

export interface AppOptions {
  logger?: boolean;
  validate?: ValidateFunction;
  validationTimeoutMs?: number;
}

class HttpError extends Error {
  constructor(
    readonly statusCode: number,
    readonly responseCode: string,
    message: string
  ) {
    super(message);
    this.name = "HttpError";
  }
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

function getErrorResponseCode(error: unknown, statusCode: number): string {
  if (statusCode === 413) return "payload_too_large";
  if (error instanceof HttpError) return error.responseCode;
  return statusCode < 500 ? "bad_request" : "internal_error";
}

function getValidationTimeoutMs(options: AppOptions): number {
  if (options.validationTimeoutMs !== undefined) return options.validationTimeoutMs;

  const raw = process.env.VALIDATION_TIMEOUT_MS;
  if (raw === undefined) return DEFAULT_VALIDATION_TIMEOUT_MS;

  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_VALIDATION_TIMEOUT_MS;
  return Math.floor(parsed);
}

function withValidationTimeout<T>(operation: Promise<T>, timeoutMs: number): Promise<T> {
  let timeout: ReturnType<typeof setTimeout> | undefined;
  const timeoutPromise = new Promise<never>((_resolve, reject) => {
    timeout = setTimeout(() => {
      reject(
        new HttpError(
          503,
          "validation_timeout",
          `Validation exceeded ${timeoutMs} ms.`
        )
      );
    }, timeoutMs);
  });

  return Promise.race([operation, timeoutPromise]).finally(() => {
    if (timeout) clearTimeout(timeout);
  });
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

    const errorCode = getErrorResponseCode(error, statusCode);
    const message =
      error instanceof HttpError
        ? error.message
        : statusCode >= 500
          ? "Internal server error."
          : error instanceof Error
            ? error.message
            : "Unknown error";
    reply.status(statusCode).send({
      error: errorCode,
      message
    });
  });

  app.get("/healthz", async (): Promise<HealthResponse> => {
    const version = getVersionInfo();
    return {
      ok: true,
      service: version.service.name,
      version: version.service.version
    };
  });

  app.get("/v1/capabilities", async (): Promise<CapabilitiesResponse> => ({
    languages: [
      { id: "sysml", extensions: [".sysml"] },
      { id: "kerml", extensions: [".kerml"] }
    ],
    validationChecks: ["all", "none"],
    standardLibrary: ["none"]
  }));

  app.get("/v1/version", async (): Promise<VersionResponse> => getVersionInfo());

  app.post("/v1/validate", async (request) => {
    const payload = validateRequestSchema.parse(request.body);
    rejectDuplicateDocumentUris(payload);
    return withValidationTimeout(
      (options.validate ?? validateSysML)(payload),
      getValidationTimeoutMs(options)
    );
  });

  return app;
}
