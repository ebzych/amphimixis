import fs from "fs";
import { unlink, mkdir } from "fs/promises";
import yaml from "yaml";
import { test, expect, describe } from "bun:test";
import path from "path";
import tool from "../tools/amphimixis.analyze.ts";

/**
 * Test running amphimixis analyzer
 */
describe("Analyzing tool", () => {
  test("analyzing function", async () => {
    const tmpDirPath = "/tmp/amphimixis/tests/opencode/analyze";
    const tmpProjPath = path.join(tmpDirPath, "proj");
    unlink(tmpProjPath).catch(() => {});
    mkdir(tmpDirPath, { recursive: true });
    const testsPath = path.join(tmpProjPath, "tests");
    const makefilePath = path.join(tmpProjPath, "Makefile");
    mkdir(testsPath, { recursive: true });
    mkdir(makefilePath, { recursive: true });
    console.log(tmpProjPath);
    let output = await tool.execute({ projectPath: tmpProjPath });
    console.log(output);
    expect(output.includes("is correct")).toBe(true);
  });
});
