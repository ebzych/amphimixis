import {tool} from '@opencode-ai/plugin';

const amixis = '__TEMPLATE_STRING_FOR_PATH_TO_AMIXIS_TO_BE_INSERTED_AT_INSTALLATION__'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function validate(args: any): Promise<string> {
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
