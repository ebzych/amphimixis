import { tool } from "@opencode-ai/plugin";
import process from "process";
import path from "path";

export async function validate(args: any): Promise<string> {
  const config_dir =
    process.env.XDG_CONFIG_HOME != undefined
      ? process.env.XDG_CONFIG_HOME
      : path.join(process.env.HOME as string, ".config");
  const opencode_tools_dir = path.join(config_dir, "opencode", "tools");
  const amixis = path.join(opencode_tools_dir, ".venv", "bin", "amixis");
  const configPath =
    args.configFilePath == undefined ? "input.yml" : args.configFilePath;
  let cmd = [amixis, "validate", "--config", configPath];

  const result = await Bun.$`${cmd}`.text();
  return result.trim();
}

export default tool({
  description: "Check the Amphimixis configuration file for correctness",
  args: {
    configFilePath: tool.schema
      .string()
      .optional()
      .describe(
        "The path to the configuration file for validation, `input.yml` by default",
      ),
  },
  async execute(args) {
    return validate(args);
  },
});
