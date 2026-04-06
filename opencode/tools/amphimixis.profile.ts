import { tool } from "@opencode-ai/plugin"
import path from "path"
import process from "process"
import fs from "fs"
import { spawn } from "child_process"

function getVenvCommand(opencode_tools_dir: string): string {
    return path.join(opencode_tools_dir, ".venv/bin/amixis")
}

export default tool({
    description: "Profile project executables with time, perf-stat and perf-record",
    args: {
        project_path: tool.schema.string().optional().describe("Path to repository of project to profile (default: current directory)"),
        config: tool.schema.string().optional().describe("Path to config file (input.yml). If not specified, checks for input.yml in project directory"),
        build_system_name: tool.schema.string().optional().describe("Build system name (cmake/meson/make/ninja/bazel). If config not provided, defaults to cmake"),
        runner_name: tool.schema.string().optional().describe("Runner name (make/ninja). If config not provided, defaults to make"),
        config_flags: tool.schema.string().optional().describe("Configuration flags for build system (e.g., -DCMAKE_BUILD_TYPE=Release)"),
        compiler_flags: tool.schema.string().array().optional().describe("List of compiler flags. Format: --<lang>_flags <flags> (e.g., --cxx_flags -O2 --c_flags -O2)"),
        toolchain_attributes: tool.schema.string().array().optional().describe("List of toolchain compilers. Format: --<tool> <path> (e.g., --cxx_compiler /usr/bin/g++ --c_compiler /usr/bin/gcc)"),
        sysroot: tool.schema.string().optional().describe("Path to sysroot for toolchain"),
        executables: tool.schema.string().array().optional().describe("List of paths to executable files to profile"),
        events: tool.schema.string().array().optional().describe("List of perf events to record (e.g., cycles cache-misses branch-misses)"),
    },
    async execute(args) {
        const projectPath = args.project_path || process.cwd()
        const inputYmlPath = path.join(projectPath, "input.yml")

        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const venv_python = path.join(opencode_tools_dir, ".venv/bin/python")

        let configArg = ""
        let eventsArg: string[] = []

        if (args.config) {
            configArg = `--config=${args.config}`
        } else if (fs.existsSync(inputYmlPath)) {
            configArg = `--config=${inputYmlPath}`
        }

        if (args.events && args.events.length > 0) {
            eventsArg = ["--events", ...args.events]
        }

        const env = {
            ...process.env,
            PYTHONPATH: opencode_tools_dir,
        }

        const amixisPath = path.join(opencode_tools_dir, "amixis.py")

        const cmdArgs = ["--build", "--profile", ...(configArg ? configArg.split(" ") : []), ...eventsArg, projectPath]

        const result = await new Promise<string>((resolve, reject) => {
            const proc = spawn(venv_python, [amixisPath, ...cmdArgs], {
                env,
                cwd: projectPath,
            })

            let stdout = ""
            let stderr = ""

            proc.stdout.on("data", (data) => {
                stdout += data.toString()
            })

            proc.stderr.on("data", (data) => {
                stderr += data.toString()
            })

            proc.on("close", (code) => {
                if (code === 0) {
                    resolve(stdout.trim())
                } else {
                    reject(new Error(stderr || stdout || `Process exited with code ${code}`))
                }
            })

            proc.on("error", reject)
        })

        return result
    },
})
