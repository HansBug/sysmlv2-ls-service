/**
 * Public request and response contracts for the service HTTP API.
 *
 * This module owns DTO shapes and schema-level validation for service-owned
 * behavior. It deliberately keeps upstream Langium and sysml-2ls object shapes
 * out of public API responses.
 *
 * @example
 * ```ts
 * const schema = makeValidateRequestSchema(DEFAULT_SERVICE_LIMITS);
 * schema.parse({ files: [{ text: "package Demo {}" }] });
 * ```
 */
import { z } from "zod";
import {
  DEFAULT_SERVICE_LIMITS,
  type HttpLimits,
  type ServiceLimits,
  type ValidateLimits,
} from "./limits.js";

/**
 * One submitted SysML/KerML document.
 *
 * The caller may identify the document with either a URI or a path. Anonymous
 * documents receive request-local memory URIs later in the adapter boundary.
 */
export const sysmlFileSchema = z.object({
  uri: z.string().min(1).optional(),
  path: z.string().min(1).optional(),
  language: z.enum(["sysml", "kerml"]).optional(),
  text: z.string(),
});

/**
 * Build the validate request schema for a concrete set of service limits.
 *
 * @param limits - Effective service-owned limits. A `null` limit disables only
 * that service-owned guard.
 * @returns Zod schema for `POST /v1/validate` request bodies.
 *
 * @example
 * ```ts
 * const schema = makeValidateRequestSchema(DEFAULT_SERVICE_LIMITS);
 * const request = schema.parse({ files: [{ text: "package Demo {}" }] });
 * ```
 */
export function makeValidateRequestSchema(limits: ServiceLimits) {
  const filesSchema =
    limits.validate.maxFiles === null
      ? z.array(sysmlFileSchema).min(1)
      : z.array(sysmlFileSchema).min(1).max(limits.validate.maxFiles);

  return z
    .object({
      files: filesSchema,
      standardLibrary: z.enum(["none"]).default("none"),
      validationChecks: z.enum(["all", "none"]).default("all"),
    })
    .superRefine((request, context) => {
      const seenUris = new Set<string>();
      let totalBytes = 0;

      request.files.forEach((file, index) => {
        const fileBytes = Buffer.byteLength(file.text, "utf8");
        totalBytes += fileBytes;

        if (
          limits.validate.maxFileTextBytes !== null &&
          fileBytes > limits.validate.maxFileTextBytes
        ) {
          context.addIssue({
            code: z.ZodIssueCode.too_big,
            type: "string",
            maximum: limits.validate.maxFileTextBytes,
            inclusive: true,
            path: ["files", index, "text"],
            message: `File text must be at most ${limits.validate.maxFileTextBytes} bytes.`,
          });
        }

        const explicitDocumentId = file.uri ?? file.path;
        if (!explicitDocumentId) return;
        if (seenUris.has(explicitDocumentId)) {
          context.addIssue({
            code: z.ZodIssueCode.custom,
            path: ["files", index, "uri"],
            message: `Duplicate file URI/path: ${explicitDocumentId}`,
          });
          return;
        }
        seenUris.add(explicitDocumentId);
      });

      if (
        limits.validate.maxTotalTextBytes !== null &&
        totalBytes > limits.validate.maxTotalTextBytes
      ) {
        context.addIssue({
          code: z.ZodIssueCode.too_big,
          type: "array",
          maximum: limits.validate.maxTotalTextBytes,
          inclusive: true,
          path: ["files"],
          message: `Total file text must be at most ${limits.validate.maxTotalTextBytes} bytes.`,
        });
      }
    });
}

/**
 * Default validate request schema using default service limits.
 */
export const validateRequestSchema = makeValidateRequestSchema(
  DEFAULT_SERVICE_LIMITS,
);

/**
 * Inferred TypeScript shape for one submitted file.
 */
export type SysMLFileInput = z.infer<typeof sysmlFileSchema>;

/**
 * Inferred TypeScript shape for a validate request.
 */
export type ValidateRequest = z.infer<typeof validateRequestSchema>;

/**
 * Zero-based source position in a diagnostic range.
 */
export interface SourcePosition {
  line: number;
  character: number;
}

/**
 * Source range attached to a normalized diagnostic.
 */
export interface SourceRange {
  start: SourcePosition;
  end: SourcePosition;
}

/**
 * Stable diagnostic severity names exposed by the service.
 */
export type DiagnosticSeverityName =
  "error" | "warning" | "information" | "hint";

/**
 * Service-owned diagnostic DTO.
 */
export interface ServiceDiagnostic {
  severity: DiagnosticSeverityName;
  source: string;
  code?: string | number;
  message: string;
  uri: string;
  range: SourceRange;
}

/**
 * Per-file validation summary returned with a validate response.
 */
export interface FileValidationSummary {
  uri: string;
  language: "sysml" | "kerml";
  parserErrors: number;
  lexerErrors: number;
  diagnostics: number;
}

/**
 * Response returned by `POST /v1/validate`.
 */
export interface ValidateResponse {
  ok: boolean;
  diagnostics: ServiceDiagnostic[];
  files: FileValidationSummary[];
  meta: {
    standardLibrary: "none";
    validationChecks: "all" | "none";
    elapsedMs: number;
  };
}

/**
 * Response returned by `GET /healthz`.
 */
export interface HealthResponse {
  ok: true;
  service: string;
  version: string;
}

/**
 * Response returned by `GET /v1/version`.
 */
export interface VersionResponse {
  service: {
    name: string;
    version: string;
    revision: string;
    sourceRepository: string;
  };
  upstream: {
    sysml2ls: {
      version: string;
      revision: string;
      packageName: string;
      repository: string;
    };
  };
  build: {
    date: string;
    nodeVersion: string;
  };
}

/**
 * Response returned by `GET /v1/capabilities`.
 */
export interface CapabilitiesResponse {
  languages: Array<{
    id: "sysml" | "kerml";
    extensions: string[];
  }>;
  validationChecks: Array<"all" | "none">;
  standardLibrary: Array<"none">;
  limits: {
    validate: ValidateLimits;
    http: HttpLimits;
  };
}
