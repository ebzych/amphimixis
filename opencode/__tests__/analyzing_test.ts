import {mkdir, writeFile} from 'fs/promises';
import {chdir} from 'process';
import {test, expect, describe} from 'bun:test';
import path from 'path';
import tool from '../tools/amphimixis.analyze';

/**
 * Test running amphimixis analyzer
 */
describe('Analyzing tool', () => {
  test('analyzing function', async () => {
    const tmpDirPath = '/tmp/amphimixis/tests/opencode/analyze';
    chdir(tmpDirPath);
    const tmpProjPath = path.join(tmpDirPath, 'proj');
    await mkdir(tmpDirPath, {recursive: true});
    await mkdir(tmpProjPath, {recursive: true});
    const testsPath = path.join(tmpProjPath, 'tests');
    const makefilePath = path.join(tmpProjPath, 'Makefile');
    await mkdir(testsPath, {recursive: true});
    await writeFile(makefilePath, 'all:\n\techo hello');
    // @ts-ignore
    const output = await tool.execute({projectPath: tmpProjPath});
    expect(output.toString().length).toBeGreaterThan(0);
  });
});
