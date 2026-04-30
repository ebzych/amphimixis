import {tool} from '@opencode-ai/plugin';
import process from 'process';
import path from 'path';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function analyze(args: any): Promise<string> {
  const configDir =
    process.env.XDG_CONFIG_HOME != undefined ?
      process.env.XDG_CONFIG_HOME :
      path.join(process.env.HOME as string, '.config');
  const opencodeToolsDir = path.join(configDir, 'opencode', 'tools');
  const amixis = path.join(opencodeToolsDir, '.venv', 'bin', 'amixis');
  let result: string = 'Internal error.';
  try {
    const output = await Bun.$`${amixis} analyze ${args.projectPath}`;
    result = output.text();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
    if (error.stdout) {
      result = error.stdout.toString();
    }
  }
  return result.trim();
}

export default tool({
  description:
    'Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems',
  args: {
    projectPath: tool.schema
        .string()
        .describe('Path to repository of analyzing project'),
  },
  async execute(args) {
    return await analyze(args);
  },
});
