import fs from 'fs';
import {unlink, mkdir} from 'fs/promises';
import yaml from 'yaml';
import {test, expect, describe} from 'bun:test';
import path from 'path';

const configureToolModule = '../tools/amphimixis.configure.ts';

const tmpDirPath = '/tmp/amphimixis/tests/opencode/configure';
const tmpConfigPath = path.join(tmpDirPath, 'input.yml');

/**
 * Test that main fields configures and numeric identification of
 * platforms and recipes works
 */
describe('Configuring tool', () => {
  test('configure function', async () => {
    try {
      await unlink(tmpConfigPath);
    } catch { /* empty */ }
    await mkdir(tmpDirPath, {recursive: true});
    const BUILD_SYSTEM = 'cmake';
    const ARCH = 'riscv';
    const CONFIG_FLAGS = '-DCMAKE_BUILD_TYPE=RelWithDebInfo';
    const BUILD_MACHINE = 'riscv-platka';

    const toolModule = await import(configureToolModule);
    const tool = toolModule.default;

    await tool.execute({
      configFilePath: tmpConfigPath,
      build_system: BUILD_SYSTEM,
      platforms: [{arch: ARCH}, {arch: ARCH}],
      recipes: [{config_flags: CONFIG_FLAGS}, {config_flags: CONFIG_FLAGS}],
      builds: [{build_machine: BUILD_MACHINE}],
    });

    const result = yaml.parse(
        fs.readFileSync(tmpConfigPath, {encoding: 'utf-8', flag: 'r'}),
    ) as {
      build_system: string;
      platforms: Array<{ id: number; arch: string }>;
      recipes: Array<{ id: number; config_flags: string }>;
      builds: Array<{ build_machine: string }>;
    };

    expect(result.build_system).toBe(BUILD_SYSTEM);
    expect(result.platforms[0].id).toBe(1);
    expect(result.platforms[0].arch).toBe(ARCH);
    expect(result.platforms[1].id).toBe(2);
    expect(result.platforms[1].arch).toBe(ARCH);
    expect(result.recipes[0].id).toBe(1);
    expect(result.recipes[0].config_flags).toBe(CONFIG_FLAGS);
    expect(result.recipes[1].id).toBe(2);
    expect(result.recipes[1].config_flags).toBe(CONFIG_FLAGS);
    expect(result.builds[0].build_machine).toBe(BUILD_MACHINE);
  });
});
