# Request-limit architecture

Limits are resolved in `src/limits.ts` and injected into Fastify and request schema validation. A `null` limit disables only the corresponding service-owned guard.
