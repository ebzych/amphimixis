import {tool} from '@opencode-ai/plugin';

export const amixis = () => 'amixis';

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
