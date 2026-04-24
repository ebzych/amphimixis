import { tool } from "@opencode-ai/plugin";
import process from "process";
import path from "path";

export default tool({
    description: 'Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems',
    args: {
        project_path: tool.schema.string().describe('Path to repository of analyzing project'),
    },
    async execute(args) {
        const config_dir = process.env.XDG_CONFIG_HOME != undefined ? process.env.XDG_CONFIG_HOME : path.join(process.env.HOME as string, '.config');
        const opencode_tools_dir = path.join(config_dir, 'opencode', 'tools');
        const amixis = path.join(opencode_tools_dir, '.venv', 'bin', 'amixis');
        let cmd = [amixis, 'analyze', args.project_path];

        const result = await Bun.$`${cmd}`.text();
        return result.trim();
    },
});
