import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";
import os from "os";

export default tool({
  description: `Build a project with specified compiler flags (optimization level, march, debug info).
Uses amphimixis build under the hood, or falls back to direct CMake/Make invocation.

RULES:
- repoPath: REQUIRED. Path to the project repository.
- optLevel: Optional. Optimization level (default: '-O3'). Examples: '-O0', '-O1', '-O2', '-O3', '-Os'.
- march: Optional. Target architecture flag (default: '-march=native'). Examples: '-march=native', '-march=rv64gc'.
- debug: Optional. Debug info flag (default: '-g'). Set to empty string to omit.
- buildTests: Optional. Whether to build tests (default: false). If true, passes -DBUILD_TESTING=ON or similar.
- configFile: Optional. Path to amphimixis config file. If not specified, auto-creates one.

EXAMPLES:
  {repoPath: '/home/user/project', optLevel: '-O3', march: '-march=native', debug: '-g', buildTests: true}
  {repoPath: '/home/user/project', optLevel: '-O2', march: '-march=rv64gc', debug: ''}`,
  args: {
    repoPath: tool.schema
      .string()
      .describe("Path to the repository to build"),
    optLevel: tool.schema
      .string()
      .optional()
      .default("-O3")
      .describe("Optimization level (e.g., -O0, -O1, -O2, -O3, -Os)"),
    march: tool.schema
      .string()
      .optional()
      .default("-march=native")
      .describe("Architecture flag (e.g., -march=native, -march=rv64gc)"),
    debug: tool.schema
      .string()
      .optional()
      .default("-g")
      .describe("Debug info flag (e.g., -g, empty string to omit)"),
    buildTests: tool.schema
      .boolean()
      .optional()
      .default(false)
      .describe("Whether to build tests alongside the project"),
    configFile: tool.schema
      .string()
      .optional()
      .describe("Path to amphimixis config file (input.yml). If omitted, auto-creates."),
  },
  async execute(args) {
    const repoPath = path.resolve(args.repoPath);

    if (!fs.existsSync(repoPath)) {
      return `Error: Path does not exist: ${repoPath}`;
    }

    const cxxFlags = [args.optLevel, args.march, args.debug].filter(Boolean).join(" ");
    const cFlags = [args.optLevel, args.march, args.debug].filter(Boolean).join(" ");

    const buildFlags = [
      `-DCMAKE_CXX_FLAGS="${cxxFlags}"`,
      `-DCMAKE_C_FLAGS="${cFlags}"`,
    ];

    if (args.buildTests) {
      buildFlags.push("-DBUILD_TESTING=ON");
    }

    const amixis = path.join(__filename, "../../../../../", "bin", "amixis");

    const results: string[] = [];
    results.push(`Building project: ${repoPath}`);
    results.push(`  Compiler C++ flags: ${cxxFlags}`);
    results.push(`  Compiler C flags: ${cFlags}`);
    results.push(`  Build tests: ${args.buildTests}`);
    results.push("");

    if (fs.existsSync(amixis)) {
      results.push("Using amphimixis build system...");
      try {
        const configFlag = args.configFile ? `--config=${args.configFile}` : "";
        const cmd = [amixis, "build", repoPath];
        if (configFlag) cmd.push(configFlag);
        const output = await Bun.$`${cmd}`.text();
        results.push(output.trim());
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errMsg = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push(`amphimixis build output: ${errMsg}`);
      }
    } else {
      results.push("amphimixis CLI not found — using direct CMake build...");
      const buildDir = path.join(repoPath, "build");
      if (!fs.existsSync(buildDir)) {
        fs.mkdirSync(buildDir, { recursive: true });
      }

      try {
        const configCmd = ["cmake", "-S", repoPath, "-B", buildDir, ...buildFlags];
        const configOutput = await Bun.$`${configCmd}`.text();
        results.push("--- CMake Configure ---");
        results.push(configOutput.trim());

        const buildCmd = ["cmake", "--build", buildDir, "-j", `${os.cpus().length}`];
        const buildOutput = await Bun.$`${buildCmd}`.text();
        results.push("--- CMake Build ---");
        results.push(buildOutput.trim());

        results.push("");
        results.push("BUILD SUCCESSFUL");
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errMsg = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push("BUILD FAILED");
        results.push(errMsg);
      }
    }

    return results.join("\n");
  },
});