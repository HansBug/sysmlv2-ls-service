import type { Diagnostic } from "vscode-languageserver";
import type { ServiceDiagnostic } from "./contracts.js";

const severityNames: Record<number, ServiceDiagnostic["severity"]> = {
  1: "error",
  2: "warning",
  3: "information",
  4: "hint"
};

export function normalizeDiagnostic(
  diagnostic: Diagnostic,
  uri: string,
  defaultSource = "sysml-2ls"
): ServiceDiagnostic {
  return {
    severity: severityNames[diagnostic.severity ?? 1] ?? "error",
    source: diagnostic.source ?? defaultSource,
    code: diagnostic.code,
    message: diagnostic.message,
    uri,
    range: diagnostic.range
  };
}
