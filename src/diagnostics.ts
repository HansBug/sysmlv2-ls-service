/**
 * Diagnostic normalization boundary.
 *
 * The service accepts diagnostics from Langium/upstream sysml-2ls and maps
 * them into stable service-owned DTOs while preserving source, code, message,
 * URI, severity, and range where available.
 *
 * @example
 * ```ts
 * const normalized = normalizeDiagnostic(diagnostic, "memory:///demo.sysml");
 * ```
 */
import type { Diagnostic } from "vscode-languageserver";
import type { ServiceDiagnostic } from "./contracts.js";

const severityNames: Record<number, ServiceDiagnostic["severity"]> = {
  1: "error",
  2: "warning",
  3: "information",
  4: "hint",
};

/**
 * Normalize one upstream diagnostic into the public service DTO.
 *
 * @param diagnostic - Langium or language-server diagnostic.
 * @param uri - Public document URI associated with the diagnostic.
 * @param defaultSource - Source value used when the upstream diagnostic omits
 * one.
 * @returns Service-owned diagnostic DTO.
 *
 * @example
 * ```ts
 * normalizeDiagnostic(diagnostic, "memory:///demo.sysml", "sysml-2ls");
 * ```
 */
export function normalizeDiagnostic(
  diagnostic: Diagnostic,
  uri: string,
  defaultSource = "sysml-2ls",
): ServiceDiagnostic {
  return {
    severity: severityNames[diagnostic.severity ?? 1] ?? "error",
    source: diagnostic.source ?? defaultSource,
    code: diagnostic.code,
    message: diagnostic.message,
    uri,
    range: diagnostic.range,
  };
}
