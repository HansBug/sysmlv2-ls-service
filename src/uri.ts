/**
 * Request-local document URI utilities.
 *
 * This module keeps URI generation and canonical duplicate checks in one place
 * so route handling and validation stay isolated from raw caller identifiers.
 *
 * @example
 * ```ts
 * const uri = makeDocumentUri({ text: "package Demo {}" }, 0);
 * ```
 */
import vscodeUri, { type URI as VscodeUri } from "vscode-uri";
import type { SysMLFileInput } from "./contracts.js";

const { URI } = vscodeUri;

/**
 * Infer SysML or KerML from explicit language or document identifier.
 *
 * @param file - Submitted file input.
 * @returns `kerml` for `.kerml` identifiers, otherwise `sysml`.
 *
 * @example
 * ```ts
 * inferLanguage({ text: "", uri: "memory:///model.kerml" });
 * ```
 */
export function inferLanguage(file: SysMLFileInput): "sysml" | "kerml" {
  if (file.language) return file.language;
  const candidate = file.uri ?? file.path ?? "";
  return candidate.toLowerCase().endsWith(".kerml") ? "kerml" : "sysml";
}

/**
 * Build the request-local Langium document URI for one file.
 *
 * @param file - Submitted file input.
 * @param index - Zero-based request file index used for anonymous documents.
 * @returns URI used inside the request-local workspace.
 *
 * @example
 * ```ts
 * makeDocumentUri({ text: "package Demo {}" }, 0).toString();
 * ```
 */
export function makeDocumentUri(
  file: SysMLFileInput,
  index: number,
): VscodeUri {
  if (file.uri) return URI.parse(file.uri);
  if (file.path) return URI.file(file.path);
  const language = inferLanguage(file);
  return URI.parse(`memory:///workspace/input-${index}.${language}`);
}

/**
 * Build the canonical duplicate-check key for one file.
 *
 * @param file - Submitted file input.
 * @param index - Zero-based request file index.
 * @returns Canonical URI string used for duplicate detection.
 *
 * @example
 * ```ts
 * makeDocumentUriKey({ text: "package Demo {}" }, 0);
 * ```
 */
export function makeDocumentUriKey(
  file: SysMLFileInput,
  index: number,
): string {
  return makeDocumentUri(file, index).toString();
}
