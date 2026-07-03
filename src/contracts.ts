import { z } from "zod";

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
