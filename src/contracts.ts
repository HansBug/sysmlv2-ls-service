import { z } from "zod";

export const MAX_FILE_TEXT_BYTES = 512 * 1024;
export const MAX_TOTAL_TEXT_BYTES = 1024 * 1024;

export const sysmlFileSchema = z.object({
  uri: z.string().min(1).optional(),
  path: z.string().min(1).optional(),
  language: z.enum(["sysml", "kerml"]).optional(),
  text: z.string()
});

export const validateRequestSchema = z.object({
  files: z.array(sysmlFileSchema).min(1).max(64),
  standardLibrary: z.enum(["none"]).default("none"),
  validationChecks: z.enum(["all", "none"]).default("all")
}).superRefine((request, context) => {
  const seenUris = new Set<string>();
  let totalBytes = 0;

  request.files.forEach((file, index) => {
    const fileBytes = Buffer.byteLength(file.text, "utf8");
    totalBytes += fileBytes;

    if (fileBytes > MAX_FILE_TEXT_BYTES) {
      context.addIssue({
        code: z.ZodIssueCode.too_big,
        type: "string",
        maximum: MAX_FILE_TEXT_BYTES,
        inclusive: true,
        path: ["files", index, "text"],
        message: `File text must be at most ${MAX_FILE_TEXT_BYTES} bytes.`
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

  if (totalBytes > MAX_TOTAL_TEXT_BYTES) {
    context.addIssue({
      code: z.ZodIssueCode.too_big,
      type: "array",
      maximum: MAX_TOTAL_TEXT_BYTES,
      inclusive: true,
      path: ["files"],
      message: `Total file text must be at most ${MAX_TOTAL_TEXT_BYTES} bytes.`
    });
  }
});

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

export interface CapabilitiesResponse {
  languages: Array<{
    id: "sysml" | "kerml";
    extensions: string[];
  }>;
  validationChecks: Array<"all" | "none">;
  standardLibrary: Array<"none">;
}
