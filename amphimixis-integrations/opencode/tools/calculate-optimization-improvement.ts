import { tool } from '@opencode-ai/plugin';
import fs from 'fs';

export default tool({
  description:
    'Calculate optimization improvement percentage.'
    + ' Formula: improvement_pct = (optimized_value / baseline_value) * 100',
  args: {
    baseline_value: tool.schema
      .number()
      .describe('Baseline measurement value (before optimization)'),
    optimized_value: tool.schema
      .number()
      .describe('Optimized measurement value (after optimization)'),
    parameter: tool.schema
      .string()
      .describe('Measured parameter name (e.g. "real_time", "user_time", "IPC")'),
    executable: tool.schema
      .string()
      .describe('Executable name the measurement belongs to'),
    baseline_build: tool.schema
      .string()
      .describe('Build name for the baseline measurement'),
    optimized_build: tool.schema
      .string()
      .describe('Build name for the optimized measurement'),
  },
  async execute(args) {
    const fileName = 'improvements.json';
    const improvementPct = (args.optimized_value / args.baseline_value) * 100;
    let data;
    try {
      data = JSON.parse(fs.readFileSync(fileName, 'utf-8'));
    } catch {
      // If the file doesn't exist or is not valid JSON, create a new object
      data = [];
    }

    data.push(
      {
        parameter: args.parameter,
        executable: args.executable,
        baseline_build: args.baseline_build,
        optimized_build: args.optimized_build,
        baseline_value: args.baseline_value,
        optimized_value: args.optimized_value,
        improvement_pcnt: Math.round(improvementPct * 100) / 100, // Round to 2 decimal places
      },
    );

    await Bun.write(fileName, JSON.stringify(data, null, 2));

    return `Improvement: ${improvementPct.toFixed(2)}%`;
  },
});
