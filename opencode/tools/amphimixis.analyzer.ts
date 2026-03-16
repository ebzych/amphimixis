import { tool } from "@opencode-ai/plugin"
import path from "path"
import process from "process"

export default tool({
    description: "Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems",
    args: {
        project_path: tool.schema.string().describe("Path to repository of analyzing project"),
    },
    async execute(args) {
        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const script = path.join(opencode_tools_dir, "amphimixis/analyzer.py")
        const result = await Bun.$`PYTHONPATH=${opencode_tools_dir} python3 ${script} ${args.project_path}`.text()
        return result.trim()
    },
})
