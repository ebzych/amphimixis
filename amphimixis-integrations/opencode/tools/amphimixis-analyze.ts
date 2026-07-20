import {tool} from '@opencode-ai/plugin';

export const amixis = () => '__TEMPLATE_STRING_FOR_PATH_TO_AMIXIS_TO_BE_INSERTED_AT_INSTALLATION__';

export default tool({
  description:
    'Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems',
  args: {
    projectPath: tool.schema
        .string()
        .describe('Path to repository of analyzing project'),
  },
  async execute(args) {
    const cmd = [amixis(), 'analyze', args.projectPath];
    return (await Bun.$`${cmd}`.text()).trim();
  },
});
