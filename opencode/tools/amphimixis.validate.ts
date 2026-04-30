import {tool} from '@opencode-ai/plugin';
import process from 'process';
import path from 'path';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function validate(args: any): Promise<string> {
  const configDir =
    process.env.XDG_CONFIG_HOME != undefined ?
      process.env.XDG_CONFIG_HOME :
      path.join(process.env.HOME as string, '.config');
  const opencodeToolsDir = path.join(configDir, 'opencode', 'tools');
  const amixis = path.join(opencodeToolsDir, '.venv', 'bin', 'amixis');
  let result: string = 'Internal error.';
  try {
    const output = await Bun.$`${amixis} validate ${args.configFilePath}`;
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
  description: 'Check the Amphimixis configuration file for correctness',
  args: {
    configFilePath: tool.schema
        .string()
        .describe(
            'The path to the configuration file for validation (path to `input.yml`)',
        ),
  },
  async execute(args) {
    return await validate(args);
  },
});
