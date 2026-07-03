import { performance } from "node:perf_hooks";
import {
  ast,
  createSysMLServices,
  type SysMLConfig
} from "syside-languageserver";
import { SysMLNodeFileSystem } from "syside-languageserver/lib/node/node-file-system-provider.js";
import type { LangiumDocument } from "langium";
import type {
  FileValidationSummary,
  ValidateRequest,
  ValidateResponse
} from "./contracts.js";
import { normalizeDiagnostic } from "./diagnostics.js";
import { inferLanguage, makeDocumentUri } from "./uri.js";

function makeConfig(): Partial<SysMLConfig> {
  return {
    standardLibrary: false,
    skipWorkspaceInit: true,
    logStatistics: false,
    defaultBuildOptions: {
      standalone: false,
      standardLibrary: "none",
      validationChecks: "all",
      ignoreMetamodelErrors: false
    }
  };
}

export async function validateSysML(request: ValidateRequest): Promise<ValidateResponse> {
  const start = performance.now();
  const services = createSysMLServices(SysMLNodeFileSystem, makeConfig());
  const factory = services.shared.workspace.LangiumDocumentFactory;
  const documents: Array<LangiumDocument<ast.Namespace>> = request.files.map((file, index) => {
    const uri = makeDocumentUri(file, index);
    return factory.fromString<ast.Namespace>(file.text, uri);
  });

  const buildOptions = {
    standalone: request.files.length === 1,
    validationChecks: request.validationChecks,
    standardLibrary: request.standardLibrary
  } as const;

  await services.shared.workspace.DocumentBuilder.build(documents, buildOptions);

  const summaries: FileValidationSummary[] = [];
  const diagnostics = documents.flatMap((document, index) => {
    const file = request.files[index];
    const language = inferLanguage(file);
    const uri = file.uri ?? document.uri.toString();
    const parserErrors = document.parseResult.parserErrors.length;
    const lexerErrors = document.parseResult.lexerErrors.length;
    const normalized = (document.diagnostics ?? []).map((diagnostic) =>
      normalizeDiagnostic(diagnostic, uri)
    );
    summaries.push({
      uri,
      language,
      parserErrors,
      lexerErrors,
      diagnostics: normalized.length
    });
    return normalized;
  });
  const hasParseOrLexErrors = summaries.some(
    (summary) => summary.parserErrors > 0 || summary.lexerErrors > 0
  );
  const hasErrorDiagnostics = diagnostics.some((diagnostic) => diagnostic.severity === "error");

  return {
    ok: !hasParseOrLexErrors && !hasErrorDiagnostics,
    diagnostics,
    files: summaries,
    meta: {
      standardLibrary: request.standardLibrary,
      validationChecks: request.validationChecks,
      elapsedMs: Math.round((performance.now() - start) * 100) / 100
    }
  };
}
