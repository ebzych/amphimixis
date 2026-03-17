import { tool } from "@opencode-ai/plugin"
import path from "path"
import process from "process"

export default tool({
    description: "Build project by simple scenario: configure with build system and then run building. Return log of building",
    args: {
        project_path: tool.schema.string().describe("Path to repository of building project"),
        build_system_name: tool.schema.string().describe("Name of build system"),
        runner_name: tool.schema.string().describe("Name of running low-level build system as Make and Ninja"),
        config_flags: tool.schema.string().describe("Configuration flags for build system. If not specified, \
use \"\""),
        compiler_flags: tool.schema.string().array().describe("List of compiler flags for specific language. Format: \
--<language>_flags <specified_flags>. If not specified, use \"\""),
        toolchain_attributes: tool.schema.string().array().describe("List of toolchain compilers for specific languages \
and toolchain tools as objdump. Format: --<<language>_compiler | <tool_name>> </path/to/it>. If not specified, use \"\""),
        sysroot: tool.schema.string().describe("Path to sysroot for toolchain. If not specified, use \"\""),
    },
    async execute(args) {
        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, ".config")
        const opencode_tools_dir = path.join(config_dir, "opencode/tools")
        const script = path.join(opencode_tools_dir, "amphimixis/builder.py")
        const result = await Bun.$`PYTHONPATH=${opencode_tools_dir} \
python ${script} ${args.project_path} ${args.build_system_name} \
${args.runner_name} ${args.config_flags} ${args.compiler_flags.join(' ')} \
${args.toolchain_attributes.join(' ')} ${args.sysroot}`.text()
        return result.trim()
    },
})
