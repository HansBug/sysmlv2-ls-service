/**
 * Production server entry point.
 *
 * The module reads runtime host, port, and logger settings from the environment,
 * builds the Fastify app, and starts listening. Application construction stays
 * in `app.ts` so tests and Docker smoke checks can reuse the same route wiring.
 *
 * @example
 * ```bash
 * PORT=3000 HOST=127.0.0.1 node dist/src/server.js
 * ```
 */
import { buildApp } from "./app.js";

const port = Number.parseInt(process.env.PORT ?? "3000", 10);
const host = process.env.HOST ?? "0.0.0.0";

const app = await buildApp({ logger: process.env.LOGGER !== "false" });

try {
  await app.listen({ port, host });
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
