/**
 * Fastify application factory and route wiring.
 *
 * This module owns HTTP behavior: CORS, request body limits, service error
 * mapping, request schema parsing, duplicate canonical URI rejection, timeout
 * handling, and route registration.
 *
 * @example
 * ```ts
 * const app = await buildApp({ logger: false });
 * await app.ready();
 * ```
 */
import Fastify, { type FastifyInstance } from "fastify";
import cors from "@fastify/cors";
import { ZodError } from "zod";
import {
  type CapabilitiesResponse,
  type HealthResponse,
  type ValidateRequest,
  type ValidateResponse,
  type VersionResponse,
  makeValidateRequestSchema,
} from "./contracts.js";
import {
  fastifyBodyLimit,
  resolveServiceLimits,
  type ServiceLimits,
} from "./limits.js";
import { validateSysML } from "./sysml-validator.js";
import { makeDocumentUriKey } from "./uri.js";
import { getVersionInfo } from "./version.js";

/**
 * Validator callback used by the Fastify route and by tests or embedders.
 *
 * @param request - Parsed validate request DTO.
 * @returns Validation response DTO.
 */
export type ValidateFunction = (
  request: ValidateRequest,
) => Promise<ValidateResponse>;

/**
 * Application construction options.
 */
export interface AppOptions {
  /** Enable or disable Fastify logging. */
  logger?: boolean;
  /** Optional validate function used by tests or embedding callers. */
  validate?: ValidateFunction;
  /** Effective service limits. Omit to resolve them from environment. */
  limits?: ServiceLimits;
}

class HttpError extends Error {
  constructor(
    readonly statusCode: number,
    readonly responseCode: string,
    message: string,
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

function withValidationTimeout<T>(
  operation: Promise<T>,
  timeoutMs: number,
): Promise<T> {
  let timeout: ReturnType<typeof setTimeout>;
  const timeoutPromise = new Promise<never>((_resolve, reject) => {
    timeout = setTimeout(() => {
      reject(
        new HttpError(
          503,
          "validation_timeout",
          `Validation exceeded ${timeoutMs} ms.`,
        ),
      );
    }, timeoutMs);
  });

  return Promise.race([operation, timeoutPromise]).finally(() => {
    clearTimeout(timeout);
  });
}

function rejectDuplicateDocumentUris(payload: ValidateRequest): void {
  const seenUris = new Set<string>();
  payload.files.forEach((file, index) => {
    const documentUri = makeDocumentUriKey(file, index);
    if (seenUris.has(documentUri)) {
      throw new ZodError([
        {
          code: "custom",
          path: ["files", index, "uri"],
          message: `Duplicate canonical file URI: ${documentUri}`,
        },
      ]);
    }
    seenUris.add(documentUri);
  });
}

/**
 * Build a configured Fastify application.
 *
 * @param options - Optional app construction settings.
 * @returns Ready-to-start Fastify application instance.
 *
 * @example
 * ```ts
 * const app = await buildApp({ logger: false });
 * const response = await app.inject({ method: "GET", url: "/healthz" });
 * ```
 */
export async function buildApp(
  options: AppOptions = {},
): Promise<FastifyInstance> {
  const limits = options.limits ?? resolveServiceLimits();
  const validateRequestSchema = makeValidateRequestSchema(limits);

  const app = Fastify({
    logger: options.logger ?? true,
    bodyLimit: fastifyBodyLimit(limits),
  });

  await app.register(cors, {
    origin: false,
  });

  app.setErrorHandler((error, _request, reply) => {
    const statusCode = getErrorStatusCode(error);

    if (error instanceof ZodError) {
      reply.status(400).send({
        error: "bad_request",
        message: "Request body failed schema validation.",
        issues: error.issues,
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
      message,
    });
  });

  app.get("/healthz", async (): Promise<HealthResponse> => {
    const version = getVersionInfo();
    return {
      ok: true,
      service: version.service.name,
      version: version.service.version,
    };
  });

  app.get("/v1/capabilities", async (): Promise<CapabilitiesResponse> => ({
    languages: [
      { id: "sysml", extensions: [".sysml"] },
      { id: "kerml", extensions: [".kerml"] },
    ],
    validationChecks: ["all", "none"],
    standardLibrary: ["none"],
    limits,
  }));

  app.get("/v1/version", async (): Promise<VersionResponse> =>
    getVersionInfo(),
  );

  app.post("/v1/validate", async (request) => {
    const payload = validateRequestSchema.parse(request.body);
    rejectDuplicateDocumentUris(payload);
    const operation = (options.validate ?? validateSysML)(payload);
    return limits.validate.validationTimeoutMs === null
      ? operation
      : withValidationTimeout(operation, limits.validate.validationTimeoutMs);
  });

  return app;
}
