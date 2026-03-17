import { tool } from "@opencode-ai/plugin"
import path from "path"
import process from "process"

export default tool({
    description: "Project project executable files with time, perf-stat and perf-record.",
    args: {
        project_path: tool.schema.string().describe("Path to repository of building project"),
        executables: tool.schema.string().array().describe("List of paths of project executable files"),
    },
    async execute(args) {
        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const script = path.join(opencode_tools_dir, "amphimixis/profiler.py")
        const result = await Bun.$`PYTHONPATH=${opencode_tools_dir} \
python ${script} ${args.project_path} ${args.executables.join(' ')}`.text()
        return result.trim()
    },
})
