import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

const VECTOR_INSTRUCTIONS_BY_ARCH: Record<string, string[]> = {
  x86: [
    "addps", "addpd", "subps", "subpd", "mulps", "mulpd",
    "divps", "divpd", "sqrtps", "sqrtpd",
    "movaps", "movapd", "movups", "movupd",
    "andps", "andpd", "orps", "orpd", "xorps", "xorpd",
    "shufps", "shufpd", "unpcklps", "unpckhps",
    "paddb", "paddw", "paddd", "paddq",
    "psubb", "psubw", "psubd", "psubq",
    "pmullw", "pmulld", "pmulhw",
  ],
  avx: [
    "vaddps", "vaddpd", "vsubps", "vsubpd",
    "vmulps", "vmulpd", "vdivps", "vdivpd",
    "vsqrtps", "vsqrtpd",
    "vmovaps", "vmovapd", "vmovups", "vmovupd",
    "vandps", "vandpd", "vorps", "vorpd", "vxorps", "vxorpd",
    "vshufps", "vshufpd",
    "vpaddb", "vpaddw", "vpaddd", "vpaddq",
    "vpsubb", "vpsubw", "vpsubd", "vpsubq",
    "vpmullw", "vpmulld", "vpmulhw",
    "vfmadd", "vfnmadd",
  ],
  avx512: [
    "vaddps", "vaddpd", "vmulps", "vmulpd",
    "vmovaps", "vmovapd",
    "vpaddd", "vpaddq", "vpsubd", "vpsubq",
    "vpmulld", "vpmullq",
    "vfmadd132", "vfmadd213", "vfmadd231",
    "vcompress", "vexpand", "vperm",
    "vpconflict", "vplzcnt",
  ],
  neon: [
    "vadd", "vsub", "vmul", "vdiv",
    "vld1", "vst1", "vld2", "vst2",
    "vmla", "vmls", "vfma", "vfms",
    "vabs", "vneg", "vsqrt",
    "vmax", "vmin", "vpadd",
    "vzip", "vuzp", "vtrn",
    "vrev", "vext", "vtbl",
  ],
  rvv: [
    "vsetvli", "vsetvl",
    "vle8", "vle16", "vle32", "vle64",
    "vse8", "vse16", "vse32", "vse64",
    "vadd", "vsub", "vmul", "vdiv",
    "vfmul", "vfadd", "vfsub", "vfdiv",
    "vslideup", "vslidedown",
    "vrgather", "vcompress",
    "vpopc", "vfirst", "vmv",
  ],
};

export default tool({
  description: `Use objdump to analyze a built binary for platform-specific vector instructions.
Helps determine if the compiler auto-vectorized code or if manual intrinsics were used.

RULES:
- binaryPath: REQUIRED. Path to the built executable or object file.
- arch: Optional. Target architecture (x86, avx, avx512, neon, rvv).
  If omitted, attempts to auto-detect from the binary.
- Returns count and listing of vector instructions found.

EXAMPLES:
  {binaryPath: './build/bin/my_app', arch: 'rvv'}
  {binaryPath: './build/bin/benchmark', arch: 'x86'}`,
  args: {
    binaryPath: tool.schema
      .string()
      .describe("Path to the built executable or object file"),
    arch: tool.schema
      .string()
      .optional()
      .describe("Target architecture (x86, avx, avx512, neon, rvv)"),
  },
  async execute(args) {
    const binaryPath = path.resolve(args.binaryPath);

    if (!fs.existsSync(binaryPath)) {
      return `Error: Binary not found: ${binaryPath}`;
    }

    const results: string[] = [];
    results.push(`=== Vector instruction analysis ===`);
    results.push(`  Binary: ${binaryPath}`);
    results.push("");

    // Determine which instruction tables to check
    const archsToCheck = args.arch
      ? [args.arch.toLowerCase()]
      : Object.keys(VECTOR_INSTRUCTIONS_BY_ARCH);

    // Run objdump
    let objdumpOutput: string;
    try {
      objdumpOutput = await Bun.$`objdump -d ${binaryPath}`.text();
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : String(e);
      return `Error running objdump: ${errMsg}`;
    }

    const lines = objdumpOutput.split("\n");
    results.push(`  Total instruction lines: ${lines.length}`);
    results.push("");

    for (const arch of archsToCheck) {
      const instructions = VECTOR_INSTRUCTIONS_BY_ARCH[arch];
      if (!instructions) {
        results.push(`  Unknown architecture: ${arch}`);
        continue;
      }

      const found: { inst: string; count: number }[] = [];

      for (const inst of instructions) {
        const count = lines.filter((l) => l.includes(inst)).length;
        if (count > 0) {
          found.push({ inst, count });
        }
      }

      const totalCount = found.reduce((sum, f) => sum + f.count, 0);
      results.push(`--- ${arch.toUpperCase()} (${found.length} unique / ${totalCount} total) ---`);
      if (found.length > 0) {
        found.sort((a, b) => b.count - a.count);
        for (const f of found) {
          results.push(`  ${f.inst}: ${f.count}`);
        }
      } else {
        results.push("  No vector instructions detected.");
      }
      results.push("");
    }

    // Summary assessment
    results.push("=== Assessment ===");
    const totalAllInstructions = Object.entries(VECTOR_INSTRUCTIONS_BY_ARCH)
      .filter(([arch]) => archsToCheck.includes(arch))
      .reduce((sum, [, insts]) => {
        return sum + insts.reduce((s, inst) => {
          return s + lines.filter((l) => l.includes(inst)).length;
        }, 0);
      }, 0);

    if (totalAllInstructions === 0) {
      results.push("  No vector instructions found. The binary may not be vectorized.");
      results.push("  Consider: -ftree-vectorize compiler flag, newer toolchain, or manual intrinsics.");
    } else {
      results.push(`  Found ${totalAllInstructions} vector instructions across ${archsToCheck.length} architecture set(s).`);
      results.push("  The binary contains vectorized code.");
    }

    return results.join("\n");
  },
});