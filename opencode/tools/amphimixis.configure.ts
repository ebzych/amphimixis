import { tool } from "@opencode-ai/plugin";
import process from "process";
import fs from "fs";
import YAML from "yaml";
import path from "path";

function addIdField(objs: object[]): void {
  let counter: number = 1;
  for (let i = 0; i < objs.length; ++i) {
    Reflect.defineProperty(objs[i], "id", { value: counter, enumerable: true });
    counter += 1;
  }
}

function sanitizeForYaml(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== "object") return obj;
  if (Array.isArray(obj)) return obj.map(sanitizeForYaml);
  const result: Record<string, any> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value !== "function" && typeof value !== "symbol") {
      result[key] = sanitizeForYaml(value);
    }
  }
  return result;
}

const configPath: string = path.join(process.cwd(), "input.yml");

export function configure(args: any): string {
  const config: Record<string, unknown> = {};
  if (args.build_system && typeof args.build_system === "string") {
    config.build_system = args.build_system;
  }
  if (args.runner && typeof args.runner === "string") {
    config.runner = args.runner;
  }
  if (args.platforms && Array.isArray(args.platforms)) {
    addIdField(args.platforms);
    config.platforms = args.platforms;
  }
  if (args.recipes && Array.isArray(args.recipes)) {
    addIdField(args.recipes);
    config.recipes = args.recipes;
  }
  if (args.builds && Array.isArray(args.builds)) {
    config.builds = args.builds;
  }
  const yamlContent = YAML.stringify(sanitizeForYaml(config));
  fs.writeFileSync(configPath, yamlContent, { encoding: "utf-8" });
  return `Config file created at ${configPath}`;
}

export default tool({
  description:
    "Create a YAML config file for Amphimixis based on provided parameters (all parameters are optional)",
  args: {
    build_system: tool.schema
      .string()
      .optional()
      .describe("(Available values: cmake, make) Build system name"),
    runner: tool.schema
      .string()
      .optional()
      .describe(
        "(Available values: make, ninja) Low-level build (running) system name",
      ),
    platforms: tool.schema
      .array(
        tool.schema.object({
          id: tool.schema
            .number()
            .int()
            .describe("Unique identificator for machine"),
          arch: tool.schema
            .string()
            .describe(
              "(Available values: riscv, x86, arm) Architecture of machine processor",
            ),
          address: tool.schema
            .string()
            .optional()
            .describe("Address of platform in network"),
          username: tool.schema
            .string()
            .optional()
            .describe("Username for authentication on machine"),
          port: tool.schema
            .number()
            .int()
            .optional()
            .describe("Port for connection to machine"),
          password: tool.schema
            .string()
            .optional()
            .describe("Password for authentication on machine"),
        }),
      )
      .optional()
      .describe(
        "List of platforms (machines) configurations to build and profile on their",
      ),
    recipes: tool.schema
      .array(
        tool.schema.object({
          config_flags: tool.schema
            .string()
            .describe("Flags for build system configuration"),
          jobs: tool.schema
            .number()
            .int()
            .optional()
            .describe("Number of parallel jobs to building project"),
          toolchain: tool.schema
            .object({
              ar: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain ar (archive tool for toolchain)",
                ),
              as: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain as (assembler tool for toolchain)",
                ),
              ld: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain ld (linker and downloader for toolchain)",
                ),
              nm: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain nm (tool for getting symbols from object file)",
                ),
              objcopy: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain objcopy (tool for copying object file)",
                ),
              objdump: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain objdump (tool for getting information from object file)",
                ),
              ranlib: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain ranlib (tool for static libraries)",
                ),
              readelf: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain readelf (tool for getting info about ELF of executable file)",
                ),
              strip: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to toolchain strip (tool for removing degub information from object file)",
                ),
              c_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to C compiler"),
              cxx_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to C++ compiler"),
              csharp_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to C# compiler"),
              cuda_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to CUDA compiler"),
              objc_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to Objective-C compiler",
                ),
              objcxx_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to Objective-C++ compiler",
                ),
              fortran_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to Fortran compiler"),
              hip_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to HIP compiler"),
              ispc_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to ISPC compiler"),
              swift_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to Swift compiler"),
              asm_compiler: tool.schema
                .string()
                .optional()
                .describe("Absolute path at system root to assembler"),
              asm_nasm_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to Netwide Assembler (NASM) (compiler)",
                ),
              asm_marmasm_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to Microsoft ARM Assembler (MARMASM) (compiler)",
                ),
              asm_masm_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to Microsoft Macro Assembler (MASM) (compiler)",
                ),
              asm_att_compiler: tool.schema
                .string()
                .optional()
                .describe(
                  "Absolute path at system root to AT&T Assembler (compiler)",
                ),
              c_flags: tool.schema.string().optional().describe("C flags"),
              cxx_flags: tool.schema.string().optional().describe("C++ flags"),
              csharp_flags: tool.schema
                .string()
                .optional()
                .describe("C# flags"),
              cuda_flags: tool.schema
                .string()
                .optional()
                .describe("CUDA flags"),
              objc_flags: tool.schema
                .string()
                .optional()
                .describe("Objective-C flags"),
              objcxx_flags: tool.schema
                .string()
                .optional()
                .describe("Objective-C++ flags"),
              fortran_flags: tool.schema
                .string()
                .optional()
                .describe("Fortran flags"),
              hip_flags: tool.schema.string().optional().describe("HIP flags"),
              ispc_flags: tool.schema
                .string()
                .optional()
                .describe("ISPC flags"),
              swift_flags: tool.schema
                .string()
                .optional()
                .describe("Swift flags"),
              asm_flags: tool.schema
                .string()
                .optional()
                .describe("assembler flags"),
              asm_nasm_flags: tool.schema
                .string()
                .optional()
                .describe("NASM flags"),
              asm_marmasm_flags: tool.schema
                .string()
                .optional()
                .describe("MARMASM flags"),
              asm_masm_flags: tool.schema
                .string()
                .optional()
                .describe("MASM flags"),
              asm_att_flags: tool.schema
                .string()
                .optional()
                .describe("AT&T assembler flags"),
            })
            .optional()
            .describe(
              "List of absolute paths to compilers or flags for compilers",
            ),
          compiler_flags: tool.schema
            .object({
              c_flags: tool.schema.string().optional().describe("C flags"),
              cxx_flags: tool.schema.string().optional().describe("C++ flags"),
              csharp_flags: tool.schema
                .string()
                .optional()
                .describe("C# flags"),
              cuda_flags: tool.schema
                .string()
                .optional()
                .describe("CUDA flags"),
              objc_flags: tool.schema
                .string()
                .optional()
                .describe("Objective-C flags"),
              objcxx_flags: tool.schema
                .string()
                .optional()
                .describe("Objective-C++ flags"),
              fortran_flags: tool.schema
                .string()
                .optional()
                .describe("Fortran flags"),
              hip_flags: tool.schema.string().optional().describe("HIP flags"),
              ispc_flags: tool.schema
                .string()
                .optional()
                .describe("ISPC flags"),
              swift_flags: tool.schema
                .string()
                .optional()
                .describe("Swift flags"),
              asm_flags: tool.schema
                .string()
                .optional()
                .describe("assembler flags"),
              asm_nasm_flags: tool.schema
                .string()
                .optional()
                .describe("NASM flags"),
              asm_marmasm_flags: tool.schema
                .string()
                .optional()
                .describe("MARMASM flags"),
              asm_masm_flags: tool.schema
                .string()
                .optional()
                .describe("MASM flags"),
              asm_att_flags: tool.schema
                .string()
                .optional()
                .describe("AT&T assembler flags"),
            })
            .optional()
            .describe("List of flags for compilers"),
          sysroot: tool.schema
            .string()
            .optional()
            .describe("Absolute path at system root to sysroot for toolchain"),
        }),
      )
      .optional()
      .describe("List of recipe configurations"),
    builds: tool.schema
      .array(
        tool.schema.object({
          build_machine: tool.schema
            .number()
            .int()
            .describe(
              "Number of build machine in config list of machines (platforms)",
            ),
          run_machine: tool.schema
            .number()
            .int()
            .describe("Number of run machine in config list of platforms"),
          recipe_id: tool.schema
            .number()
            .int()
            .describe("Number of recipe in config list of recipes"),
          executables: tool.schema
            .string()
            .array()
            .optional()
            .describe("List of paths to executables to profile"),
        }),
      )
      .optional()
      .describe("List of build configurations"),
  },
  async execute(args) {
    return configure(args);
  },
});
