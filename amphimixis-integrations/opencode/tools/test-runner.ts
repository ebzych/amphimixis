import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

export default tool({
  description: `Run tests for a built project and report pass/fail results.

Supports ctest (CMake), make test, and direct test executable invocation.

RULES:
- buildDir: REQUIRED. Path to the build directory containing built tests.
- testTarget: Optional. Specific test target to run (default: all tests).
- timeout: Optional. Timeout per test in seconds (default: 300).
- Returns structured test results with pass/fail counts.

EXAMPLES:
  {buildDir: '/home/user/project/build'}
  {buildDir: '/home/user/project/build', testTarget: 'test-unit', timeout: 120}`,
  args: {
    buildDir: tool.schema
      .string()
      .describe("Path to the build directory with compiled tests"),
    testTarget: tool.schema
      .string()
      .optional()
      .describe("Specific test target to run"),
    timeout: tool.schema
      .number()
      .optional()
      .default(300)
      .describe("Timeout per test in seconds"),
  },
  async execute(args) {
    const buildDir = path.resolve(args.buildDir);

    if (!fs.existsSync(buildDir)) {
      return `Error: Build directory does not exist: ${buildDir}`;
    }

    const results: string[] = [];
    results.push(`Running tests in: ${buildDir}`);
    if (args.testTarget) {
      results.push(`  Test target: ${args.testTarget}`);
    }
    results.push(`  Timeout: ${args.timeout}s`);
    results.push("");

    // Try ctest first (CMake projects)
    const ctestPath = path.join(buildDir, "CTestTestfile.cmake");
    if (fs.existsSync(ctestPath) || fs.existsSync(path.join(buildDir, "CMakeCache.txt"))) {
      results.push("=== Running ctest ===");
      try {
        const ctestCmd = ["ctest", "--test-dir", buildDir, "--output-on-failure"];
        if (args.testTarget) {
          ctestCmd.push("-R", args.testTarget);
        }
        ctestCmd.push("--timeout", String(args.timeout));

        const output = await Bun.$`${ctestCmd}`.text();
        results.push(output.trim());

        // Extract summary
        const summaryMatch = output.match(/(\d+)% tests passed, (\d+) tests failed out of (\d+)/);
        if (summaryMatch) {
          results.push("");
          results.push(`  Tests passed: ${summaryMatch[1]}`);
          results.push(`  Tests failed: ${summaryMatch[2]}`);
          results.push(`  Total tests: ${summaryMatch[3]}`);
        }
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(errOutput);
        // Parse partial results from error output
        const summaryMatch = errOutput.match(/(\d+)% tests passed, (\d+) tests failed out of (\d+)/);
        if (summaryMatch) {
          results.push("");
          results.push(`  Tests passed: ${summaryMatch[1]}`);
          results.push(`  Tests failed: ${summaryMatch[2]}`);
          results.push(`  Total tests: ${summaryMatch[3]}`);
        }
      }
    } else {
      // Try make test
      results.push("=== Running make test ===");
      try {
        const makeCmd = ["make", "-C", buildDir, "test"];
        if (args.testTarget) {
          makeCmd[2] = args.testTarget;
        }
        const output = await Bun.$`${makeCmd}`.text();
        results.push(output.trim());
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(errOutput);
      }
    }

    // Try to find and run standalone test executables if ctest/make test not available
    results.push("");
    results.push("=== Checking for standalone test executables ===");
    let testExesFound = 0;
    function findTestExes(dir: string): void {
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith(".")) {
            findTestExes(path.join(dir, entry.name));
          } else if (entry.isFile() && entry.name.startsWith("test") && entry.name.endsWith(".exe")) {
            testExesFound++;
          } else if (entry.isFile() && entry.name.startsWith("test") && !path.extname(entry.name)) {
            testExesFound++;
          }
        }
      } catch {
        // skip unreadable
      }
    }
    findTestExes(buildDir);
    results.push(`  Standalone test executables found: ${testExesFound}`);

    return results.join("\n");
  },
});