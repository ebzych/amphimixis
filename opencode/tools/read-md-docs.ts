import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
    description: "Read context of first text header with keywords from .md files",
    args: {
        file_path: tool.schema.string().describe("Path to .md file"),
        keywords: tool.schema.array().describe("List of keywords to searching")
    },
    async execute(args) {
        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const script = path.join(opencode_tools_dir, "read-md-docs.py")
        const result = await Bun.$`PYTHONPATH=${opencode_tools_dir} python3 ${script} ${args.project_path}`.text()
        return result.trim()
    },
})
