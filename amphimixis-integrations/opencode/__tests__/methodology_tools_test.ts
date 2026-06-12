import { mkdir, writeFile, rm } from "fs/promises";
import { chdir } from "process";
import { test, expect, describe } from "bun:test";
import path from "path";

const testsDir = "/tmp/amphimixis/tests/opencode/integrations";

describe("Methodology Tools", () => {
  test("repo-check-git-activity", async () => {
    const tmpDir = path.join(testsDir, "repo-check-git-activity");
    await rm(tmpDir, { recursive: true, force: true });
    await mkdir(tmpDir, { recursive: true });
    chdir(tmpDir);

    const projPath = path.join(tmpDir, "proj");
    await mkdir(projPath, { recursive: true });
    await writeFile(path.join(projPath, "README.md"), "# Test Project\n");
    await Bun.$`git -C ${projPath} init`;
    await Bun.$`git -C ${projPath} config user.email "test@test.com"`;
    await Bun.$`git -C ${projPath} config user.name "Test"`;
    await Bun.$`git -C ${projPath} add .`;
    await Bun.$`git -C ${projPath} commit -m "Initial commit"`;

    const tool = await import("../tools/repo-check-git-activity");
    const output = await tool.default.execute({ repoPath: projPath });
    expect(output.toString().length).toBeGreaterThan(0);
    expect(output.toString()).toContain("Recent Commits");
  });

  test("repo-check-readme", async () => {
    const tmpDir = path.join(testsDir, "repo-check-readme");
    await mkdir(tmpDir, { recursive: true });

    await writeFile(
      path.join(tmpDir, "README.md"),
      "# Test\nThis project was moved to https://github.com/other/project\n",
    );

    const tool = await import("../tools/repo-check-readme");
    const output = await tool.default.execute({ repoPath: tmpDir });
    expect(output.toString().length).toBeGreaterThan(0);
    expect(output.toString()).toContain("README.md");
    expect(output.toString()).toContain("moved");
  });

  test("repo-check-distro-packages", async () => {
    const tool = await import("../tools/repo-check-distro-packages");
    const output = await tool.default.execute({ projectName: "test-nonexistent-pkg-12345" });
    expect(output.toString().length).toBeGreaterThan(0);
  });

  test("project-scan-macros", async () => {
    const tmpDir = path.join(testsDir, "project-scan-macros");
    await mkdir(tmpDir, { recursive: true });

    await writeFile(
      path.join(tmpDir, "test.c"),
      '#include <stdio.h>\n#ifdef __x86_64__\nprintf("x86_64\\n");\n#endif\n#ifdef __ARM_NEON__\nprintf("neon\\n");\n#endif\n',
    );

    const tool = await import("../tools/project-scan-macros");
    const output = await tool.default.execute({ repoPath: tmpDir });
    expect(output.toString().length).toBeGreaterThan(0);
    expect(output.toString()).toContain("x86_64");
    expect(output.toString()).toContain("NEON");
  });

  test("dependency-check-portability", async () => {
    const tool = await import("../tools/dependency-check-portability");
    const output = await tool.default.execute({
      dependencyName: "yaml-cpp",
      targetArch: "riscv64",
    });
    expect(output.toString().length).toBeGreaterThan(0);
    expect(output.toString()).toContain("READY");

    const missingOutput = await tool.default.execute({
      dependencyName: "nonexistent-dep-xyz",
      targetArch: "riscv64",
    });
    expect(missingOutput.toString()).toContain("MISSING");
  });

  test("build-with-flags", async () => {
    const tmpDir = path.join(testsDir, "build-with-flags");
    await mkdir(tmpDir, { recursive: true });

    await writeFile(
      path.join(tmpDir, "Makefile"),
      "all:\n\techo 'build ok'\n",
    );

    const tool = await import("../tools/build-with-flags");
    const output = await tool.default.execute({
      repoPath: tmpDir,
      optLevel: "-O2",
    });
    expect(output.toString().length).toBeGreaterThan(0);
  });

  test("test-runner", async () => {
    const tmpDir = path.join(testsDir, "test-runner");
    await mkdir(tmpDir, { recursive: true });

    await writeFile(
      path.join(tmpDir, "Makefile"),
      "test:\n\techo 'tests passed'\n",
    );

    const tool = await import("../tools/test-runner");
    const output = await tool.default.execute({ buildDir: tmpDir });
    expect(output.toString().length).toBeGreaterThan(0);
  });

  test("check-vector-instructions", async () => {
    const tmpDir = path.join(testsDir, "check-vector-instructions");
    await mkdir(tmpDir, { recursive: true });

    // Create a simple test binary
    await writeFile(
      path.join(tmpDir, "test_binary"),
      "x0x0x0",
    );

    const tool = await import("../tools/check-vector-instructions");
    const output = await tool.default.execute({
      binaryPath: path.join(tmpDir, "test_binary"),
      arch: "x86",
    });
    expect(output.toString().length).toBeGreaterThan(0);
  });

  test("try-optimization", async () => {
    const tmpDir = path.join(testsDir, "try-optimization");
    await mkdir(tmpDir, { recursive: true });

    await writeFile(
      path.join(tmpDir, "Makefile"),
      "all:\n\techo 'build ok'\n",
    );

    const tool = await import("../tools/try-optimization");
    const output = await tool.default.execute({
      projectPath: tmpDir,
      optimizationType: "compiler_flag",
      value: "-ftree-vectorize",
    });
    expect(output.toString().length).toBeGreaterThan(0);
  });
});