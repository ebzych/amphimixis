import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";
import os from "os";

type OptimizationType = "compiler_flag" | "allocator" | "lto";

function getAllocatorFlags(allocator: string): string[] {
  switch (allocator.toLowerCase()) {
    case "mimalloc":
      return ["-DMIMALLOC=ON", "-ljemalloc"];
    case "jemalloc":
      return ["-ljemalloc"];
    case "tcmalloc":
      return ["-ltcmalloc"];
    default:
      return [];
  }
}

export default tool({
  description: `Apply an optimization technique (compiler flag, memory allocator, or LTO),
rebuild the project, and optionally profile the result for comparison.

RULES:
- projectPath: REQUIRED. Path to the project repository.
- optimizationType: REQUIRED. Type of optimization: 'compiler_flag', 'allocator', or 'lto'.
- value: REQUIRED. The optimization value:
  - For 'compiler_flag': e.g., '-ftree-vectorize', '-funroll-loops', '-ffast-math'
  - For 'allocator': one of 'mimalloc', 'jemalloc', 'tcmalloc'
  - For 'lto': 'yes' or 'full' (enables -flto)
- profileAfter: Optional. Whether to run perf stat after building (default: false).
- configFile: Optional. Path to amphimixis config file.

EXAMPLES:
  {projectPath: '/home/user/project', optimizationType: 'compiler_flag', value: '-ftree-vectorize'}
  {projectPath: '/home/user/project', optimizationType: 'allocator', value: 'mimalloc', profileAfter: true}
  {projectPath: '/home/user/project', optimizationType: 'lto', value: 'full'}`,
  args: {
    projectPath: tool.schema
      .string()
      .describe("Path to the project repository"),
    optimizationType: tool.schema
      .string()
      .describe("Type of optimization: 'compiler_flag', 'allocator', or 'lto'"),
    value: tool.schema
      .string()
      .describe("The optimization value (flag, allocator name, or 'yes'/'full' for LTO)"),
    profileAfter: tool.schema
      .boolean()
      .optional()
      .default(false)
      .describe("Whether to run perf stat after building"),
    configFile: tool.schema
      .string()
      .optional()
      .describe("Path to amphimixis config file"),
  },
  async execute(args) {
    const projectPath = path.resolve(args.projectPath);

    if (!fs.existsSync(projectPath)) {
      return `Error: Project path does not exist: ${projectPath}`;
    }

    const validTypes: OptimizationType[] = ["compiler_flag", "allocator", "lto"];
    if (!validTypes.includes(args.optimizationType as OptimizationType)) {
      return `Error: Invalid optimization type: ${args.optimizationType}. Valid types: ${validTypes.join(", ")}`;
    }

    const results: string[] = [];
    results.push(`=== Optimization Attempt ===`);
    results.push(`  Project: ${projectPath}`);
    results.push(`  Type: ${args.optimizationType}`);
    results.push(`  Value: ${args.value}`);
    results.push("");

    const amixis = path.join(__filename, "../../../../../", "bin", "amixis");

    let buildFlags: string[] = [];

    switch (args.optimizationType) {
      case "compiler_flag":
        buildFlags = [`-DCMAKE_CXX_FLAGS="${args.value}"`, `-DCMAKE_C_FLAGS="${args.value}"`];
        results.push(`  Adding compiler flags: ${args.value}`);
        break;

      case "allocator":
        buildFlags = getAllocatorFlags(args.value);
        results.push(`  Using allocator: ${args.value}`);
        results.push(`  Linker flags: ${buildFlags.join(" ")}`);
        break;

      case "lto":
        buildFlags = ["-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON"];
        if (args.value === "full" || args.value === "yes") {
          buildFlags.push("-DCMAKE_CXX_FLAGS=-flto", "-DCMAKE_C_FLAGS=-flto");
        }
        results.push("  Enabling Link-Time Optimization (LTO)");
        break;
    }

    // Build using amphimixis if available
    if (fs.existsSync(amixis)) {
      try {
        const configFlag = args.configFile ? `--config=${args.configFile}` : "";
        const cmd = [amixis, "build", projectPath];
        if (configFlag) cmd.push(configFlag);
        const output = await Bun.$`${cmd}`.text();
        results.push("--- Build Output ---");
        results.push(output.trim());

        if (output.includes("FAILED") || output.includes("Error")) {
          results.push("");
          results.push("OPTIMIZATION BUILD FAILED");
          return results.join("\n");
        }
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push("--- Build Error ---");
        results.push(errOutput);
        results.push("");
        results.push("OPTIMIZATION BUILD FAILED");
        return results.join("\n");
      }
    } else {
      // Direct CMake build
      const buildDir = path.join(projectPath, "build");
      if (!fs.existsSync(buildDir)) {
        fs.mkdirSync(buildDir, { recursive: true });
      }

      try {
        const configCmd = ["cmake", "-S", projectPath, "-B", buildDir, ...buildFlags];
        const configOutput = await Bun.$`${configCmd}`.text();
        results.push("--- CMake Configure ---");
        results.push(configOutput.trim());

        const buildCmd = ["cmake", "--build", buildDir, "-j", `${os.cpus().length}`];
        const buildOutput = await Bun.$`${buildCmd}`.text();
        results.push("--- CMake Build ---");
        results.push(buildOutput.trim());
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errOutput = (e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e);
        results.push("BUILD FAILED");
        results.push(errOutput);
        return results.join("\n");
      }
    }

    results.push("");
    results.push("OPTIMIZATION BUILD SUCCESSFUL");
    results.push("");

    // Profile after build if requested
    if (args.profileAfter) {
      results.push("--- Post-optimization profiling ---");
      try {
        const buildDir = path.join(projectPath, "build");
        const entries = fs.readdirSync(buildDir, { withFileTypes: true });
        let foundExe = "";
        for (const entry of entries) {
          if (entry.isFile() && !entry.name.includes(".") && entry.name.startsWith("test")) {
            foundExe = path.join(buildDir, entry.name);
            break;
          }
        }

        if (foundExe && fs.existsSync(foundExe)) {
          try {
            const perfCmd = [
              "perf", "stat", "-ddd",
              "--repeat", "3",
              "--", foundExe,
            ];
            const perfOutput = await Bun.$`${perfCmd}`.text();
            results.push(perfOutput.trim());
          } catch (e) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            results.push((e as any).stdout?.toString() || (e as any).stderr?.toString() || String(e));
          }
        } else {
          results.push("  No suitable executable found for profiling.");
        }
      } catch (e) {
        results.push(`  Profiling error: ${e}`);
      }
    }

    return results.join("\n");
  },
});