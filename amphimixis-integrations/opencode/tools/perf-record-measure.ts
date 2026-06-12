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
  description: `Run perf record to collect execution samples, then perf report to view hotspots.
  - Pins to high-performance core via taskset
  - Sets highest priority via nice -n -20
  - Collects perf.data and runs perf report for hotspot analysis

RULES:
- executable: REQUIRED. Path to the executable to profile.
- core: Optional. CPU core to pin to (auto-detected if omitted).
- outputDir: Optional. Directory to save perf output files (default: current directory).
- args: Optional. Command-line arguments to pass to the executable.
- reportOptions: Optional. Additional perf report options (e.g., '--sort=comm,dso,symbol').

EXAMPLES:
  {executable: './build/bin/my_app', core: 0}
  {executable: './build/bin/benchmark', args: '--size=1000', reportOptions: '--sort=dso,symbol'}`,
  args: {
    executable: tool.schema
      .string()
      .describe("Path to the executable to profile"),
    core: tool.schema
      .number()
      .int()
      .optional()
      .describe("CPU core to pin to (auto-detected if omitted)"),
    outputDir: tool.schema
      .string()
      .optional()
      .describe("Directory to save perf output files"),
    args: tool.schema
      .string()
      .optional()
      .describe("Command-line arguments to pass to the executable"),
    reportOptions: tool.schema
      .string()
      .optional()
      .default("--sort=comm,dso,symbol")
      .describe("Additional perf report options"),
  },
  async execute(args) {
    const exePath = path.resolve(args.executable);

    if (!fs.existsSync(exePath)) {
      return `Error: Executable not found: ${exePath}`;
    }

    const core = args.core !== undefined ? args.core : findHighPerfCore();
    const outputDir = args.outputDir ? path.resolve(args.outputDir) : process.cwd();
    const exeArgs = args.args || "";

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const perfDataPath = path.join(outputDir, "perf.data");
    const results: string[] = [];

    results.push(`=== perf record measurement ===`);
    results.push(`  Executable: ${exePath}`);
    results.push(`  Pinned to core: ${core}`);
    results.push(`  Output dir: ${outputDir}`);
    results.push(`  perf.data: ${perfDataPath}`);
    if (exeArgs) results.push(`  Arguments: ${exeArgs}`);
    results.push("");

    // Run perf record
    results.push("--- Collecting samples (perf record) ---");
    try {
      const recordCmd = [
        "nice", "-n", "-20",
        "taskset", "-c", String(core),
        "perf", "record",
        "-o", perfDataPath,
        exePath,
        ...(exeArgs ? exeArgs.split(/\s+/) : []),
      ];

      const recordOutput = await Bun.$`${recordCmd}`.text();
      results.push(recordOutput.trim() || "(no stdout from perf record)");
      results.push(`  perf.data saved to: ${perfDataPath}`);
      results.push("");
} catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(`perf record error: ${errOutput}`);
      results.push("");
    }

    // Run perf report
    results.push("--- Hotspot Analysis (perf report) ---");
    if (fs.existsSync(perfDataPath)) {
      try {
        const reportCmd = [
          "perf", "report",
          "-i", perfDataPath,
          "--stdio",
          ...(args.reportOptions ? args.reportOptions.split(/\s+/) : []),
        ];

        const reportOutput = await Bun.$`${reportCmd}`.text();
        const reportLines = reportOutput.split("\n");

        // Include full report but cap at appropriate length
        if (reportLines.length > 200) {
          results.push("(showing first 200 lines of perf report)");
          results.push(...reportLines.slice(0, 200));
          results.push(`... (${reportLines.length - 200} more lines)`);
        } else {
          results.push(...reportLines);
        }
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(`perf report error: ${errOutput}`);
      }

      // Cleanup perf.data
      try {
        fs.unlinkSync(perfDataPath);
      } catch {
        // ignore cleanup failures
      }
    } else {
      results.push("  perf.data not found — cannot generate report.");
    }

    return results.join("\n");
  },
});