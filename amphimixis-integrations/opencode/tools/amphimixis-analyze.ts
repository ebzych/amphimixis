import {tool} from '@opencode-ai/plugin';

const amixis = '__TEMPLATE_STRING_FOR_PATH_TO_AMIXIS_TO_BE_INSERTED_AT_INSTALLATION__'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function analyze(args: any): Promise<string> {
  const cmd = [amixis, 'analyze', args.projectPath];
  return (await Bun.$`${cmd}`.text()).trim();
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
