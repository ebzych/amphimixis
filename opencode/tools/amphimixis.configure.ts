import { tool } from "@opencode-ai/plugin";
import process from "process";
import fs from "fs";
import YAML from "yaml";
import { getProtectedObjects } from "bun:jsc";

export default tool({
    description: "Create a YAML config file for Amphimixis based on provided parameters",
    args: {
        build_system: tool.schema.string().optional().describe("Build system name (cmake/make)"),
        runner: tool.schema.string().optional().describe("Runner name (make/ninja)"),
        platforms: tool.schema.array(tool.schema.object({
            id: tool.schema.number().int().describe("Unique identificator for machine"),
            arch: tool.schema.string().describe("Architecture of machine processor (riscv, x86, arm)"),
            address: tool.schema.string().optional().describe("Address of platform in network"),
            username: tool.schema.string().optional().describe("Username for authentication on machine"),
            port: tool.schema.number().int().optional().describe("Port for connection to machine"),
            password: tool.schema.string().optional().describe("Password for authentication on machine"),
        })).optional().describe("List of platforms (machines) configurations to build and profile on their"),
        recipes: tool.schema.array(tool.schema.object({
            toolchain: tool.schema.object({
                ar: tool.schema.string().optional(),
                as: tool.schema.string().optional(),
                ld: tool.schema.string().optional(),
                nm: tool.schema.string().optional(),
                objcopy: tool.schema.string().optional(),
                objdump: tool.schema.string().optional(),
                ranlib: tool.schema.string().optional(),
                readelf: tool.schema.string().optional(),
                strip: tool.schema.string().optional(),
                c_compiler: tool.schema.string().optional(),
                cxx_compiler: tool.schema.string().optional(),
                csharp_compiler: tool.schema.string().optional(),
                cuda_compiler: tool.schema.string().optional(),
                objc_compiler: tool.schema.string().optional(),
                objcxx_compiler: tool.schema.string().optional(),
                fortran_compiler: tool.schema.string().optional(),
                hip_compiler: tool.schema.string().optional(),
                ispc_compiler: tool.schema.string().optional(),
                swift_compiler: tool.schema.string().optional(),
                asm_compiler: tool.schema.string().optional(),
                asm_nasm_compiler: tool.schema.string().optional(),
                asm_marmasm_compiler: tool.schema.string().optional(),
                asm_masm_compiler: tool.schema.string().optional(),
                asm_att_compiler: tool.schema.string().optional(),
                c_flags: tool.schema.string().optional(),
                cxx_flags: tool.schema.string().optional(),
                csharp_flags: tool.schema.string().optional(),
                cuda_flags: tool.schema.string().optional(),
                objc_flags: tool.schema.string().optional(),
                objcxx_flags: tool.schema.string().optional(),
                fortran_flags: tool.schema.string().optional(),
                hip_flags: tool.schema.string().optional(),
                ispc_flags: tool.schema.string().optional(),
                swift_flags: tool.schema.string().optional(),
                asm_flags: tool.schema.string().optional(),
                asm_nasm_flags: tool.schema.string().optional(),
                asm_marmasm_flags: tool.schema.string().optional(),
                asm_masm_flags: tool.schema.string().optional(),
                asm_att_flags: tool.schema.string().optional(),
            }).optional().describe("Absolute paths to compilers"),
            sysroot: tool.schema.string().optional().describe("Absolute path to sysroot for toolchain"),
            jobs: tool.schema.number().int().optional().describe("Number of parallel jobs to building project"),
        })).optional().describe("List of recipe configurations"),
        builds: tool.schema.array(tool.schema.object({
            build_machine: tool.schema.number().int().describe("Number of build machine in config list of machines (platforms)"),
            run_machine: tool.schema.number().int().describe("Number of run machine in config list of platforms"),
            recipe_id: tool.schema.number().int().describe("Number of recipe in config list of recipes"),
            executables: tool.schema.string().array().optional().describe("List of paths to executables to profile"),
        })).optional().describe("List of build configurations"),
    },
    async execute(args) {
        const config: Record<string, unknown> = {};
        if (args.build_system) {
            config.build_system = args.build_system;
        }
        if (args.runner) {
            config.runner = args.runner;
        }
        if (args.platforms) {
            config.platforms = args.platforms;
        }
        if (args.recipes) {
            config.recipes = args.recipes;
        }
        if (args.builds) {
            config.builds = args.builds;
        }
        const yamlContent = YAML.stringify(config);
        fs.writeFileSync(process.cwd(), yamlContent);
        return `Config file created at ${process.cwd()}`;
    },
});
