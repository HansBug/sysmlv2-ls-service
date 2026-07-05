/**
 * Service-owned request limit configuration.
 *
 * Limits are resolved from environment variables for server and Docker runs,
 * or injected directly through `buildApp({ limits })` in tests and embedding
 * scenarios. A `null` value disables only that service-owned guard; it does not
 * mean the process has infinite memory or upstream work capacity.
 *
 * @example
 * ```ts
 * const limits = resolveServiceLimits({ VALIDATE_MAX_FILES: "0" });
 * limits.validate.maxFiles; // null
 * ```
 */
/** Default maximum number of files in one validate request. */
export const DEFAULT_MAX_FILES = 64;

/** Default maximum UTF-8 byte size for one file's text. */
export const DEFAULT_MAX_FILE_TEXT_BYTES = 512 * 1024;

/** Default maximum total UTF-8 byte size for all submitted files. */
export const DEFAULT_MAX_TOTAL_TEXT_BYTES = 1024 * 1024;

/** Default Fastify HTTP body limit in bytes. */
export const DEFAULT_HTTP_BODY_LIMIT_BYTES = 5 * 1024 * 1024;

/** Default validation timeout in milliseconds. */
export const DEFAULT_VALIDATION_TIMEOUT_MS = 30_000;

/**
 * Limits that apply to the validate route and validator wrapper.
 */
export interface ValidateLimits {
  maxFiles: number | null;
  maxFileTextBytes: number | null;
  maxTotalTextBytes: number | null;
  validationTimeoutMs: number | null;
}

/**
 * HTTP-level limits used by Fastify.
 */
export interface HttpLimits {
  bodyLimitBytes: number | null;
}

/**
 * Complete effective service limit set.
 */
export interface ServiceLimits {
  validate: ValidateLimits;
  http: HttpLimits;
}

/**
 * Default service-owned limits documented in the README.
 */
export const DEFAULT_SERVICE_LIMITS: ServiceLimits = {
  validate: {
    maxFiles: DEFAULT_MAX_FILES,
    maxFileTextBytes: DEFAULT_MAX_FILE_TEXT_BYTES,
    maxTotalTextBytes: DEFAULT_MAX_TOTAL_TEXT_BYTES,
    validationTimeoutMs: DEFAULT_VALIDATION_TIMEOUT_MS,
  },
  http: {
    bodyLimitBytes: DEFAULT_HTTP_BODY_LIMIT_BYTES,
  },
};

const DISABLED_VALUES = new Set(["0", "none", "unlimited"]);

function parseLimit(
  name: string,
  fallback: number,
  env: NodeJS.ProcessEnv,
): number | null {
  const raw = env[name];
  if (raw === undefined) return fallback;

  const value = raw.trim().toLowerCase();
  if (DISABLED_VALUES.has(value)) return null;

  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(
      `${name} must be a positive integer, 0, "none", or "unlimited".`,
    );
  }
  return parsed;
}

/**
 * Resolve effective service limits from environment variables.
 *
 * @param env - Environment-like object. Defaults to `process.env`.
 * @returns Effective service limits.
 * @throws Error when a configured limit is not a positive integer, `0`,
 * `"none"`, or `"unlimited"`.
 *
 * @example
 * ```ts
 * resolveServiceLimits({ HTTP_BODY_LIMIT_BYTES: "0" }).http.bodyLimitBytes;
 * ```
 */
export function resolveServiceLimits(
  env: NodeJS.ProcessEnv = process.env,
): ServiceLimits {
  return {
    validate: {
      maxFiles: parseLimit("VALIDATE_MAX_FILES", DEFAULT_MAX_FILES, env),
      maxFileTextBytes: parseLimit(
        "VALIDATE_MAX_FILE_TEXT_BYTES",
        DEFAULT_MAX_FILE_TEXT_BYTES,
        env,
      ),
      maxTotalTextBytes: parseLimit(
        "VALIDATE_MAX_TOTAL_TEXT_BYTES",
        DEFAULT_MAX_TOTAL_TEXT_BYTES,
        env,
      ),
      validationTimeoutMs: parseLimit(
        "VALIDATION_TIMEOUT_MS",
        DEFAULT_VALIDATION_TIMEOUT_MS,
        env,
      ),
    },
    http: {
      bodyLimitBytes: parseLimit(
        "HTTP_BODY_LIMIT_BYTES",
        DEFAULT_HTTP_BODY_LIMIT_BYTES,
        env,
      ),
    },
  };
}

/**
 * Convert HTTP limits into a Fastify-compatible body limit.
 *
 * @param limits - Effective service limits.
 * @returns Fastify body limit in bytes.
 *
 * @example
 * ```ts
 * fastifyBodyLimit(DEFAULT_SERVICE_LIMITS);
 * ```
 */
export function fastifyBodyLimit(limits: ServiceLimits): number {
  return limits.http.bodyLimitBytes ?? Number.MAX_SAFE_INTEGER;
}
