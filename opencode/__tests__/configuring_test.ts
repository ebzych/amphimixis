import fs from "fs";
import { unlink, mkdir } from "fs/promises";
import yaml from "yaml";
import { test, expect, describe } from "bun:test";
import { configure } from "../tools/amphimixis.configure";
import path from "path";

/**
 * Test that main fields configures and numeric identification of 
 * platforms and recipes works 
 */
describe("Configuring tool", () => {
    test("configure function", () => {
        const tmpDirPath = "/tmp/amphimixis/tests/opencode/configure";
        const tmpConfigPath = path.join(tmpDirPath, "input.yml");
        unlink(tmpConfigPath).catch(() => {});
        mkdir(tmpDirPath, { recursive: true }).catch(() => {});
        const BUILD_SYSTEM = "cmake";
        const ARCH = "riscv";
        const CONFIG_FLAGS = "-DCMAKE_BUILD_TYPE=RelWithDebInfo";
        const BUILD_MACHINE = "riscv-platka";
        configure(
            {
                build_system: BUILD_SYSTEM,
                platforms: [ { arch: ARCH }, { arch: ARCH } ],
                recipes: [ { config_flags: CONFIG_FLAGS }, { config_flags: CONFIG_FLAGS } ],
                builds: [ { build_machine: BUILD_MACHINE } ],
            },
            tmpConfigPath,
        );
        const result = yaml.parse(fs.readFileSync(tmpConfigPath, { encoding: "utf-8", flag: "r"})) as {
            build_system: string,
            platforms: Array<{ id: number, arch: string }>,
            recipes: Array<{ id: number, config_flags: string }>,
            builds: Array<{ build_machine: string }>,
        };
        let is_correct = true;
        if (result.recipes[0].id !== 1 || result.recipes[0].config_flags !== CONFIG_FLAGS ||
            result.platforms[0].id !== 1 || result.platforms[0].arch !== ARCH ||
            result.recipes[1].id !== 2 || result.recipes[1].config_flags !== CONFIG_FLAGS ||
            result.platforms[1].id !== 2 || result.platforms[1].arch !== ARCH ||
            result.builds[0].build_machine !== BUILD_MACHINE
        ) {
            is_correct = false;
        }
        console.log(result);
        console.log(result.recipes[0].id);
        expect(is_correct).toBe(true);
    });
});
