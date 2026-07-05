import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    exclude: ["dist/**", "upstream/**", "node_modules/**"],
    testTimeout: 30000,
    coverage: {
      provider: "v8",
      include: [
        "src/app.ts",
        "src/contracts.ts",
        "src/diagnostics.ts",
        "src/limits.ts",
        "src/sysml-validator.ts",
        "src/uri.ts",
        "src/version.ts"
      ],
      reporter: ["text", "lcov", "cobertura"],
      thresholds: {
        branches: 100,
        functions: 100,
        lines: 100,
        statements: 100
      }
    }
  }
});
