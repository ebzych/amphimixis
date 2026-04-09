import { tool } from "@opencode-ai/plugin"
import path from "path"
import process from "process"
import fs from "fs"
import { spawn } from "child_process"

function getVenvCommand(opencode_tools_dir: string): string {
    return path.join(opencode_tools_dir, ".venv/bin/amixis")
}

export default tool({
    description: "Build project by simple scenario: configure with build system and then run building. Return log of building",
    args: {
        project_path: tool.schema.string().describe("Path to repository of building project"),
        config: tool.schema.string().optional().describe("Path to config file. If not specified, checks for input.yml in current directory or automatically create it"),
        build_system_name: tool.schema.string().optional().describe("Build system name (cmake/make)"),
        runner_name: tool.schema.string().optional().describe("Runner name (make/ninja)"),
        config_flags: tool.schema.string().optional().describe("Configuration flags for build system (e.g., -DCMAKE_BUILD_TYPE=Release)"),
        compiler_flags: tool.schema.string().array().optional().describe("List of compiler flags. Format: --<lang>_flags <flags> (e.g., --cxx_flags '-O2' --c_flags '-O2')"),
        toolchain_attributes: tool.schema.string().array().optional().describe("List of toolchain compilers. Format: --<tool> <absolute_path> (e.g., --cxx_compiler /usr/bin/g++ --c_compiler /usr/bin/gcc)"),
        sysroot: tool.schema.string().optional().describe("Absolute path to sysroot for toolchain"),
        executables: tool.schema.string().array().optional().describe("List of paths to executable files to build"),
    },
    async execute(args) {
        const projectPath = args.project_path || process.cwd()
        const inputYmlPath = path.join(projectPath, "input.yml")

        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const venv_python = path.join(opencode_tools_dir, ".venv/bin/python")

        let configArg = ""

        if (args.config) {
            configArg = `--config=${args.config}`
        } else if (fs.existsSync(inputYmlPath)) {
            configArg = `--config=${inputYmlPath}`
        }

        const env = {
            ...process.env,
            PYTHONPATH: opencode_tools_dir,
        }

        const amixisPath = path.join(opencode_tools_dir, "amixis.py")

        const cmdArgs = ["--build", ...(configArg ? configArg.split(" ") : []), projectPath]

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
