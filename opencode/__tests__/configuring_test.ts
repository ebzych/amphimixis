import fs from "fs";
import { unlink, mkdir } from "fs/promises";
import yaml from "yaml";
import { test, expect, describe, mock } from "bun:test";
import tool from "../tools/amphimixis.configure";
import path from "path";

const configureToolModule = "../tools/amphimixis.configure.ts";

const tmpDirPath = "/tmp/amphimixis/tests/opencode/configure";
const tmpConfigPath = path.join(tmpDirPath, "input.yml");
mock.module(configureToolModule, () => {
  return {
    tool: tool,
    configPath: tmpConfigPath,
  };
});

/**
 * Test that main fields configures and numeric identification of
 * platforms and recipes works
 */
describe("Configuring tool", () => {
  test("configure function", async () => {
    unlink(tmpConfigPath).catch(() => {});
    mkdir(tmpDirPath, { recursive: true });
    const BUILD_SYSTEM = "cmake";
    const ARCH = "riscv";
    const CONFIG_FLAGS = "-DCMAKE_BUILD_TYPE=RelWithDebInfo";
    const BUILD_MACHINE = "riscv-platka";
    const execute = import(configureToolModule).tool.execute;
    execute(
      {
        build_system: BUILD_SYSTEM,
        platforms: [{ arch: ARCH }, { arch: ARCH }],
        recipes: [
          { config_flags: CONFIG_FLAGS },
          { config_flags: CONFIG_FLAGS },
        ],
        builds: [{ build_machine: BUILD_MACHINE }],
      },
      "",
    );
    const result = yaml.parse(
      fs.readFileSync(tmpConfigPath, { encoding: "utf-8", flag: "r" }),
    ) as {
      build_system: string;
      platforms: Array<{ id: number; arch: string }>;
      recipes: Array<{ id: number; config_flags: string }>;
      builds: Array<{ build_machine: string }>;
    };
    let isCorrect = true;
    if (
      result.recipes[0].id !== 1 ||
      result.recipes[0].config_flags !== CONFIG_FLAGS ||
      result.platforms[0].id !== 1 ||
      result.platforms[0].arch !== ARCH ||
      result.recipes[1].id !== 2 ||
      result.recipes[1].config_flags !== CONFIG_FLAGS ||
      result.platforms[1].id !== 2 ||
      result.platforms[1].arch !== ARCH ||
      result.builds[0].build_machine !== BUILD_MACHINE
    ) {
      isCorrect = false;
    }
    expect(isCorrect).toBe(true);
  });
});
