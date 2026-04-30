import { tool } from "@opencode-ai/plugin";
import process from "process";
import path from "path";

export async function analyze(args: any): Promise<string> {
  const amixis = path.join(__dirname, ".venv", "bin", "amixis");
  const result = await Bun.$`${amixis} analyze ${args.projectPath}`.text();
  return result.trim();
}

export default tool({
  description:
    "Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems",
  args: {
    projectPath: tool.schema
      .string()
      .describe("Path to repository of analyzing project"),
  },
  async execute(args) {
    return await analyze(args);
  },
});
