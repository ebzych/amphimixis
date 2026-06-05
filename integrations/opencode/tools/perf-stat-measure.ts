import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";
import os from "os";

function findHighPerfCore(): number {
  try {
    const cpus = os.cpus();
    let maxFreq = 0;
    let bestCore = 0;
    for (let i = 0; i < cpus.length; i++) {
      if (cpus[i].speed > maxFreq) {
        maxFreq = cpus[i].speed;
        bestCore = i;
      }
    }
    return bestCore;
  } catch {
    return 0;
  }
}

export default tool({
  description: `Run perf stat with -ddd on an executable with proper experimental rigor:
  - Pin to high-performance core via taskset
  - Set highest priority via nice -n -20
  - Perform warmup runs
  - Repeat N times for statistical significance
  - Generate table output when using --repeat

RULES:
- executable: REQUIRED. Path to the executable to profile.
- core: Optional. CPU core to pin to (auto-detected as highest frequency core if omitted).
- warmupRuns: Optional. Number of warmup runs (default: 3, which is ~10% of 30 total).
- totalRuns: Optional. Total measurement runs (default: 10, must be >= 6 for statistical significance).
- args: Optional. Command-line arguments to pass to the executable.
- Returns perf stat metrics including elapsed time, cache-misses, branches, branch-misses.

EXAMPLES:
  {executable: './build/bin/my_app', core: 0, warmupRuns: 3, totalRuns: 10}
  {executable: './build/bin/benchmark', args: '--size=1000', totalRuns: 6}`,
  args: {
    executable: tool.schema
      .string()
      .describe("Path to the executable to profile"),
    core: tool.schema
      .number()
      .int()
      .optional()
      .describe("CPU core to pin to (auto-detected if omitted)"),
    warmupRuns: tool.schema
      .number()
      .int()
      .optional()
      .default(3)
      .describe("Number of warmup runs"),
    totalRuns: tool.schema
      .number()
      .int()
      .optional()
      .default(10)
      .describe("Total measurement runs (minimum 6 recommended)"),
    args: tool.schema
      .string()
      .optional()
      .describe("Command-line arguments to pass to the executable"),
  },
  async execute(args) {
    const exePath = path.resolve(args.executable);

    if (!fs.existsSync(exePath)) {
      return `Error: Executable not found: ${exePath}`;
    }

    const core = args.core !== undefined ? args.core : findHighPerfCore();
    const exeArgs = args.args || "";
    const totalRuns = Math.max(args.totalRuns, 6);

    const results: string[] = [];
    results.push(`=== perf stat measurement ===`);
    results.push(`  Executable: ${exePath}`);
    results.push(`  Pinned to core: ${core}`);
    results.push(`  Warmup runs: ${args.warmupRuns}`);
    results.push(`  Measurement runs: ${totalRuns}`);
    if (exeArgs) results.push(`  Arguments: ${exeArgs}`);
    results.push("");

    // Warmup phase
    if (args.warmupRuns > 0) {
      results.push(`--- Warmup (${args.warmupRuns} runs) ---`);
      for (let i = 0; i < args.warmupRuns; i++) {
        try {
          const warmupCmd = [
            "nice", "-n", "-20",
            "taskset", "-c", String(core),
            exePath,
            ...(exeArgs ? exeArgs.split(/\s+/) : []),
          ];
          await Bun.$`${warmupCmd}`.text();
        } catch {
          // warmup failures are acceptable
        }
      }
      results.push("  Warmup complete.");
      results.push("");
    }

    // Measurement phase
    results.push(`--- Measurement (${totalRuns} runs) ---`);
    try {
      const perfCmd = [
        "nice", "-n", "-20",
        "taskset", "-c", String(core),
        "perf", "stat", "-ddd",
        "--repeat", String(totalRuns),
        ...(exeArgs ? ["--", exePath, ...exeArgs.split(/\s+/)] : ["--", exePath]),
      ];

      const output = await Bun.$`${perfCmd}`.text();
      results.push(output.trim());

      // Parse key metrics
      results.push("");
      results.push("--- Key Metrics Summary ---");
      const lines = output.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (
          trimmed.includes("time elapsed") ||
          trimmed.includes("cache-misses") ||
          trimmed.includes("branches") ||
          trimmed.includes("branch-misses") ||
          trimmed.includes("instructions") ||
          trimmed.includes("cycles") ||
          trimmed.includes("context-switches") ||
          trimmed.includes("page-faults")
        ) {
          results.push(`  ${trimmed}`);
        }
      }
} catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(errOutput);

      // Try without --table if it failed
      results.push("");
      results.push("Retrying without --table option...");
      try {
        const perfCmdSimple = [
          "nice", "-n", "-20",
          "taskset", "-c", String(core),
          "perf", "stat", "-ddd",
          exePath,
          ...(exeArgs ? exeArgs.split(/\s+/) : []),
        ];
        const outputSimple = await Bun.$`${perfCmdSimple}`.text();
        results.push(outputSimple.trim());
      } catch (e2) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        results.push((e2 as any).stdout?.toString() || (e2 as any).stderr?.toString() || String(e2));
      }
    }

    return results.join("\n");
  },
});