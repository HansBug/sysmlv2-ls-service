import { describe, expect, it } from "vitest";
import { inferLanguage, makeDocumentUri, makeDocumentUriKey } from "../src/uri.js";

describe("document URI helpers", () => {
  it("infers languages from explicit language, URI, path, or default", () => {
    expect(inferLanguage({ text: "", language: "kerml" })).toBe("kerml");
    expect(inferLanguage({ text: "", uri: "memory:///model.kerml" })).toBe("kerml");
    expect(inferLanguage({ text: "", path: "/tmp/model.SYSML" })).toBe("sysml");
    expect(inferLanguage({ text: "" })).toBe("sysml");
  });

  it("builds document URIs from uri, path, or generated memory ids", () => {
    expect(makeDocumentUri({ text: "", uri: "memory:///given.sysml" }, 0).toString()).toBe(
      "memory:/given.sysml"
    );
    expect(makeDocumentUri({ text: "", path: "/tmp/given.sysml" }, 1).toString()).toBe(
      "file:///tmp/given.sysml"
    );
    expect(makeDocumentUri({ text: "", language: "kerml" }, 2).toString()).toBe(
      "memory:/workspace/input-2.kerml"
    );
    expect(makeDocumentUriKey({ text: "" }, 3)).toBe("memory:/workspace/input-3.sysml");
  });
});
