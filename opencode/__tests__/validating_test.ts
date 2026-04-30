import fs from "fs";
import path from "path";
import { unlink, mkdir } from "fs/promises";
import yaml from "yaml";
import { test, expect, describe } from "bun:test";
import { context } from "@opencode-ai/plugin";
import tool from "../tools/amphimixis.validate.ts";

/**
 * Test running amphimixis validator
 */
describe("Validating config file tool", () => {
  test("validating function", async () => {
    const tmpDirPath = "/tmp/amphimixis/tests/opencode/validate";
    const tmpConfigPath = path.join(tmpDirPath, "input.yml");
    unlink(tmpConfigPath).catch(() => {});
    mkdir(tmpDirPath, { recursive: true }).catch(() => {});
    const BUILD_SYSTEM = "cmake";
    const RUNNER = "ninja";
    const ARCH = "riscv";
    const CONFIG_FLAGS = "-DCMAKE_BUILD_TYPE=RelWithDebInfo";
    const MACHINE = "riscv-platka";
    fs.writeFileSync(
      tmpConfigPath,
      yaml.stringify({
        build_system: BUILD_SYSTEM,
        runner: RUNNER,
        platforms: [
          {
            id: 1,
            arch: ARCH,
          },
          {
            id: 2,
            arch: ARCH,
          },
        ],
        recipes: [
          {
            id: 1,
            config_flags: CONFIG_FLAGS,
          },
        ],
        builds: [
          {
            build_machine: 1,
            run_machine: 2,
            recipe_id: 1,
          },
        ],
      }),
    );
    let output = await tool.execute({ configFilePath: tmpConfigPath }, context);
    expect(output.includes("is correct")).toBe(true);
  });
});
