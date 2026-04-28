import { tool } from "@opencode-ai/plugin";
import path from "path";
import process from "process";

export default tool({
  description:
    "Build project by simple scenario: configure with build system and then run building. Return log of building",
  args: {
    project_path: tool.schema
      .string()
      .describe("Path to repository of building project"),
    config: tool.schema
      .string()
      .optional()
      .describe(
        "Path to config file. If not specified, checks for input.yml in current directory or automatically create it",
      ),
  },
  async execute(args) {
    const config_dir =
      process.env.XDG_CONFIG_HOME != undefined
        ? process.env.XDG_CONFIG_HOME
        : path.join(process.env.HOME as string, ".config");
    const opencode_tools_dir = path.join(config_dir, "opencode", "tools");
    const amixis = path.join(opencode_tools_dir, ".venv", "bin", "amixis");
    let cmd = [amixis, "build", args.project_path];
    if (args.config) cmd.push(`--config=${args.config}`);

    const result = await Bun.$`${cmd}`.text();
    return result.trim();
  },
});
