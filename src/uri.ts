import vscodeUri, { type URI as VscodeUri } from "vscode-uri";
import type { SysMLFileInput } from "./contracts.js";

const { URI } = vscodeUri;

export function inferLanguage(file: SysMLFileInput): "sysml" | "kerml" {
  if (file.language) return file.language;
  const candidate = file.uri ?? file.path ?? "";
  return candidate.toLowerCase().endsWith(".kerml") ? "kerml" : "sysml";
}

export function makeDocumentUri(file: SysMLFileInput, index: number): VscodeUri {
  if (file.uri) return URI.parse(file.uri);
  if (file.path) return URI.file(file.path);
  const language = inferLanguage(file);
  return URI.parse(`memory:///workspace/input-${index}.${language}`);
}

export function makeDocumentUriKey(file: SysMLFileInput, index: number): string {
  return makeDocumentUri(file, index).toString();
}
