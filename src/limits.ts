export const DEFAULT_MAX_FILES = 64;
export const DEFAULT_MAX_FILE_TEXT_BYTES = 512 * 1024;
export const DEFAULT_MAX_TOTAL_TEXT_BYTES = 1024 * 1024;
export const DEFAULT_HTTP_BODY_LIMIT_BYTES = 5 * 1024 * 1024;
export const DEFAULT_VALIDATION_TIMEOUT_MS = 30_000;

export interface ValidateLimits {
  maxFiles: number | null;
  maxFileTextBytes: number | null;
  maxTotalTextBytes: number | null;
  validationTimeoutMs: number | null;
}

export interface HttpLimits {
  bodyLimitBytes: number | null;
}

export interface ServiceLimits {
  validate: ValidateLimits;
  http: HttpLimits;
}

export const DEFAULT_SERVICE_LIMITS: ServiceLimits = {
  validate: {
    maxFiles: DEFAULT_MAX_FILES,
    maxFileTextBytes: DEFAULT_MAX_FILE_TEXT_BYTES,
    maxTotalTextBytes: DEFAULT_MAX_TOTAL_TEXT_BYTES,
    validationTimeoutMs: DEFAULT_VALIDATION_TIMEOUT_MS
  },
  http: {
    bodyLimitBytes: DEFAULT_HTTP_BODY_LIMIT_BYTES
  }
};

const DISABLED_VALUES = new Set(["0", "none", "unlimited"]);

function parseLimit(name: string, fallback: number, env: NodeJS.ProcessEnv): number | null {
  const raw = env[name];
  if (raw === undefined) return fallback;

  const value = raw.trim().toLowerCase();
  if (DISABLED_VALUES.has(value)) return null;

  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(
      `${name} must be a positive integer, 0, "none", or "unlimited".`
    );
  }
  return parsed;
}

export function resolveServiceLimits(env: NodeJS.ProcessEnv = process.env): ServiceLimits {
  return {
    validate: {
      maxFiles: parseLimit("VALIDATE_MAX_FILES", DEFAULT_MAX_FILES, env),
      maxFileTextBytes: parseLimit(
        "VALIDATE_MAX_FILE_TEXT_BYTES",
        DEFAULT_MAX_FILE_TEXT_BYTES,
        env
      ),
      maxTotalTextBytes: parseLimit(
        "VALIDATE_MAX_TOTAL_TEXT_BYTES",
        DEFAULT_MAX_TOTAL_TEXT_BYTES,
        env
      ),
      validationTimeoutMs: parseLimit(
        "VALIDATION_TIMEOUT_MS",
        DEFAULT_VALIDATION_TIMEOUT_MS,
        env
      )
    },
    http: {
      bodyLimitBytes: parseLimit(
        "HTTP_BODY_LIMIT_BYTES",
        DEFAULT_HTTP_BODY_LIMIT_BYTES,
        env
      )
    }
  };
}

export function fastifyBodyLimit(limits: ServiceLimits): number {
  return limits.http.bodyLimitBytes ?? Number.MAX_SAFE_INTEGER;
}
