/**
 * Validates that the generated Python API reference rendered Sphinx/reST docstrings.
 *
 * The Python client uses reStructuredText field lists in source docstrings. This
 * script guards the MkDocs/mkdocstrings integration by failing when the built
 * reference page leaks raw Sphinx markers into browser-facing HTML.
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

const htmlPath = join(
  process.cwd(),
  "site",
  "reference",
  "python",
  "index.html",
);
const html = readFileSync(htmlPath, "utf8");

const forbiddenMarkers = [
  ":param",
  ":type",
  ":return",
  ":rtype",
  ":raises",
  ":class:",
  ":func:",
  ":mod:",
  ":meth:",
  ":attr:",
  "Example::",
  "+----------------",
  "Module roadmap",
];

const requiredMarkers = [
  '<span class="doc-section-title">Parameters',
  '<span class="doc-section-title">Returns',
  '<span class="doc-section-title">Raises',
  "sysmlv2slclient.client.SysMLV2LSClient",
  "collect_directory_files",
];

const leakedMarkers = forbiddenMarkers.filter((marker) =>
  html.includes(marker),
);
const missingMarkers = requiredMarkers.filter(
  (marker) => !html.includes(marker),
);

if (leakedMarkers.length || missingMarkers.length) {
  if (leakedMarkers.length) {
    console.error(
      `Python reference leaked raw reStructuredText markers: ${leakedMarkers.join(", ")}`,
    );
  }
  if (missingMarkers.length) {
    console.error(
      `Python reference is missing expected rendered API markers: ${missingMarkers.join(", ")}`,
    );
  }
  process.exit(1);
}
