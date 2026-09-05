import path from 'node:path';
import {tool} from '@opencode-ai/plugin';

export const amixis = () => {
  const installed = '$AMIXIS_PATH';
  return installed === '$AMIXIS_PATH' ? 'amixis' : installed;
};

export default tool({
  description:
    'Analyze project repository: find CI, tests, benchmarks, dependencies, documentation, build systems',
  args: {
    projectPath: tool.schema
        .string()
        .describe('Path to repository of analyzing project'),
  },
  async execute(args) {
    const projectDir = path.isAbsolute(args.projectPath)
      ? args.projectPath
      : `./${path.basename(args.projectPath)}`;
    const cmd = [amixis(), 'analyze', args.projectPath];
    return (await Bun.$.cwd(projectDir)`${cmd}`.text()).trim();
  },
});