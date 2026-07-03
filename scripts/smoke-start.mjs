import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const port = 3010;
const child = spawn(process.execPath, ["dist/src/server.js"], {
  env: { ...process.env, PORT: String(port), LOGGER: "false" },
  stdio: ["ignore", "pipe", "pipe"]
});

let output = "";
child.stdout.on("data", (chunk) => {
  output += chunk.toString();
});
child.stderr.on("data", (chunk) => {
  output += chunk.toString();
});

const stop = async () => {
  if (child.exitCode === null) {
    child.kill("SIGTERM");
    await delay(250);
  }
};

try {
  let response;
  for (let attempt = 0; attempt < 30; attempt += 1) {
    if (child.exitCode !== null) {
      throw new Error(`server exited early with code ${child.exitCode}\n${output}`);
    }
    try {
      response = await fetch(`http://127.0.0.1:${port}/healthz`);
      if (response.ok) break;
    } catch {
      await delay(250);
    }
  }

  if (!response?.ok) {
    throw new Error(`server did not become healthy\n${output}`);
  }

  const body = await response.json();
  if (body.ok !== true || body.service !== "sysmlv2-ls-service") {
    throw new Error(`unexpected health response: ${JSON.stringify(body)}`);
  }

  const versionResponse = await fetch(`http://127.0.0.1:${port}/v1/version`);
  if (!versionResponse.ok) {
    throw new Error(`version endpoint failed with ${versionResponse.status}\n${output}`);
  }
  const versionBody = await versionResponse.json();
  if (
    versionBody.service?.name !== "sysmlv2-ls-service" ||
    versionBody.upstream?.sysml2ls?.packageName !== "syside-languageserver"
  ) {
    throw new Error(`unexpected version response: ${JSON.stringify(versionBody)}`);
  }
} finally {
  await stop();
}
