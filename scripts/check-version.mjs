import { readFileSync } from "node:fs";
import { URL } from "node:url";

const packageJson = JSON.parse(
  readFileSync(new URL("../package.json", import.meta.url), "utf8"),
);
const version = readFileSync(
  new URL("../VERSION", import.meta.url),
  "utf8",
).trim();
const semverPattern =
  /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;

if (!semverPattern.test(version)) {
  throw new Error(
    `VERSION must be a semantic version, got ${JSON.stringify(version)}`,
  );
}

if (packageJson.version !== version) {
  throw new Error(
    `VERSION (${version}) must match package.json version (${packageJson.version})`,
  );
}

console.log(`Version check passed: ${version}`);
