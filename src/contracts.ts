import { z } from "zod";
import {
  DEFAULT_SERVICE_LIMITS,
  type HttpLimits,
  type ServiceLimits,
  type ValidateLimits
} from "./limits.js";

export const sysmlFileSchema = z.object({
  uri: z.string().min(1).optional(),
  path: z.string().min(1).optional(),
  language: z.enum(["sysml", "kerml"]).optional(),
  text: z.string()
});

export function makeValidateRequestSchema(limits: ServiceLimits) {
  const filesSchema =
    limits.validate.maxFiles === null
      ? z.array(sysmlFileSchema).min(1)
      : z.array(sysmlFileSchema).min(1).max(limits.validate.maxFiles);

  return z.object({
    files: filesSchema,
    standardLibrary: z.enum(["none"]).default("none"),
    validationChecks: z.enum(["all", "none"]).default("all")
  }).superRefine((request, context) => {
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
          message: `File text must be at most ${limits.validate.maxFileTextBytes} bytes.`
        });
      }

      const explicitDocumentId = file.uri ?? file.path;
      if (!explicitDocumentId) return;
      if (seenUris.has(explicitDocumentId)) {
        context.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["files", index, "uri"],
          message: `Duplicate file URI/path: ${explicitDocumentId}`
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
        message: `Total file text must be at most ${limits.validate.maxTotalTextBytes} bytes.`
      });
    }
  });
}

export const validateRequestSchema = makeValidateRequestSchema(DEFAULT_SERVICE_LIMITS);

export type SysMLFileInput = z.infer<typeof sysmlFileSchema>;
export type ValidateRequest = z.infer<typeof validateRequestSchema>;

export interface SourcePosition {
  line: number;
  character: number;
}

export interface SourceRange {
  start: SourcePosition;
  end: SourcePosition;
}

export type DiagnosticSeverityName = "error" | "warning" | "information" | "hint";

export interface ServiceDiagnostic {
  severity: DiagnosticSeverityName;
  source: string;
  code?: string | number;
  message: string;
  uri: string;
  range: SourceRange;
}

export interface FileValidationSummary {
  uri: string;
  language: "sysml" | "kerml";
  parserErrors: number;
  lexerErrors: number;
  diagnostics: number;
}

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

export interface HealthResponse {
  ok: true;
  service: string;
  version: string;
}

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
