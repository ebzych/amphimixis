import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

const ARCH_MACROS = [
  { macro: "__x86_64__", arch: "x86_64", description: "x86-64 architecture" },
  { macro: "__i386__", arch: "x86", description: "x86 (32-bit) architecture" },
  { macro: "__amd64__", arch: "amd64", description: "AMD64 architecture" },
  { macro: "__arm__", arch: "arm", description: "ARM architecture" },
  { macro: "__aarch64__", arch: "aarch64", description: "ARM 64-bit architecture" },
  { macro: "__riscv", arch: "riscv", description: "RISC-V architecture" },
  { macro: "__riscv64", arch: "riscv64", description: "RISC-V 64-bit" },
  { macro: "__powerpc__", arch: "powerpc", description: "PowerPC architecture" },
  { macro: "__s390x__", arch: "s390x", description: "IBM Z architecture" },
  { macro: "__mips__", arch: "mips", description: "MIPS architecture" },
  { macro: "__sparc__", arch: "sparc", description: "SPARC architecture" },
  { macro: "__alpha__", arch: "alpha", description: "Alpha architecture" },
];

const VECTORIZATION_MACROS = [
  { macro: "__SSE__", isa: "SSE", description: "SSE intrinsics" },
  { macro: "__SSE2__", isa: "SSE2", description: "SSE2 intrinsics" },
  { macro: "__SSE3__", isa: "SSE3", description: "SSE3 intrinsics" },
  { macro: "__SSSE3__", isa: "SSSE3", description: "SSSE3 intrinsics" },
  { macro: "__SSE4_1__", isa: "SSE4.1", description: "SSE4.1 intrinsics" },
  { macro: "__SSE4_2__", isa: "SSE4.2", description: "SSE4.2 intrinsics" },
  { macro: "__AVX__", isa: "AVX", description: "AVX intrinsics" },
  { macro: "__AVX2__", isa: "AVX2", description: "AVX2 intrinsics" },
  { macro: "__AVX512F__", isa: "AVX-512", description: "AVX-512 Foundation" },
  { macro: "__AVX512BW__", isa: "AVX-512", description: "AVX-512 Byte/Word" },
  { macro: "__AVX512DQ__", isa: "AVX-512", description: "AVX-512 DQ" },
  { macro: "__AVX512VL__", isa: "AVX-512", description: "AVX-512 VL" },
  { macro: "__ARM_NEON__", isa: "NEON", description: "ARM NEON intrinsics" },
  { macro: "__ARM_NEON", isa: "NEON", description: "ARM NEON intrinsics (alt)" },
  { macro: "__RISCV_VECTOR", isa: "RVV", description: "RISC-V Vector extension" },
  { macro: "__riscv_v", isa: "RVV", description: "RISC-V Vector extension (alt)" },
  { macro: "__ALTIVEC__", isa: "AltiVec", description: "PowerPC AltiVec" },
  { macro: "__VSX__", isa: "VSX", description: "PowerPC VSX" },
];

const PLATFORM_MACROS = [
  { macro: "_WIN32", platform: "Windows", description: "Windows platform" },
  { macro: "_WIN64", platform: "Windows", description: "Windows 64-bit" },
  { macro: "__APPLE__", platform: "macOS", description: "Apple platform" },
  { macro: "__linux__", platform: "Linux", description: "Linux platform" },
  { macro: "__unix__", platform: "Unix", description: "Unix platform" },
  { macro: "__FreeBSD__", platform: "FreeBSD", description: "FreeBSD platform" },
  { macro: "__ANDROID__", platform: "Android", description: "Android platform" },
];

const INTRINSIC_PATTERNS = [
  { pattern: "_mm_", isa: "SSE/SSE2", description: "SSE intrinsic function" },
  { pattern: "_mm256_", isa: "AVX", description: "AVX intrinsic function" },
  { pattern: "_mm512_", isa: "AVX-512", description: "AVX-512 intrinsic function" },
  { pattern: "vint8", isa: "RVV", description: "RVV vector type" },
  { pattern: "vint16", isa: "RVV", description: "RVV vector type" },
  { pattern: "vint32", isa: "RVV", description: "RVV vector type" },
  { pattern: "vint64", isa: "RVV", description: "RVV vector type" },
  { pattern: "vfloat32", isa: "RVV", description: "RVV vector type" },
  { pattern: "vfloat64", isa: "RVV", description: "RVV vector type" },
  { pattern: "neon", isa: "NEON", description: "NEON reference" },
  { pattern: "vec_", isa: "AltiVec", description: "AltiVec intrinsic" },
];

function findFiles(dir: string, extensions: string[], maxFiles: number = 200): string[] {
  const results: string[] = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (results.length >= maxFiles) break;
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (
          !entry.name.startsWith(".") &&
          entry.name !== "node_modules" &&
          entry.name !== "build" &&
          entry.name !== ".git"
        ) {
          results.push(...findFiles(fullPath, extensions, maxFiles - results.length));
        }
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (extensions.includes(ext)) {
          results.push(fullPath);
        }
      }
    }
  } catch {
    // permission denied, skip
  }
  return results;
}

export default tool({
  description: `Scan project source code for architecture-specific macros, vectorization intrinsics,
and platform-dependent preprocessor directives. This helps assess portability to different architectures.

RULES:
- repoPath is REQUIRED.
- Scans .c, .h, .cpp, .hpp, .cc, .hh, .cxx, .hxx, .s, .S, .asm files.
- Reports all found macros with file locations and line numbers.
- Separate sections for architecture macros, vectorization macros, platform macros, and intrinsics.

EXAMPLES:
  {repoPath: '/home/user/project'}`,
  args: {
    repoPath: tool.schema
      .string()
      .describe("Path to the repository to scan"),
  },
  async execute(args) {
    const repoPath = path.resolve(args.repoPath);

    if (!fs.existsSync(repoPath)) {
      return `Error: Path does not exist: ${repoPath}`;
    }

    const sourceExtensions = [
      ".c", ".h", ".cpp", ".hpp", ".cc", ".hh",
      ".cxx", ".hxx", ".s", ".S", ".asm",
    ];

    const files = findFiles(repoPath, sourceExtensions);
    const results: string[] = [];
    results.push(`Scanning ${files.length} source files for platform-specific macros...`);
    results.push("");

    const archHits: { macro: string; arch: string; file: string; line: number }[] = [];
    const vectorHits: { macro: string; isa: string; file: string; line: number }[] = [];
    const platformHits: { macro: string; platform: string; file: string; line: number }[] = [];
    const intrinsicHits: { pattern: string; isa: string; file: string; line: number }[] = [];

    for (const file of files) {
      try {
        const content = fs.readFileSync(file, { encoding: "utf-8" });
        const lines = content.split("\n");

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const relPath = path.relative(repoPath, file);

          for (const am of ARCH_MACROS) {
            const macroRegex = new RegExp(`#ifdef\\s+${am.macro}|#if\\s+defined\\s*\\(\\s*${am.macro}\\s*\\)|#if\\s+.*${am.macro}`, "i");
            if (macroRegex.test(line)) {
              archHits.push({ macro: am.macro, arch: am.arch, file: relPath, line: i + 1 });
            }
          }

          for (const vm of VECTORIZATION_MACROS) {
            const macroRegex = new RegExp(`#ifdef\\s+${vm.macro}|#if\\s+defined\\s*\\(\\s*${vm.macro}\\s*\\)|#if\\s+.*${vm.macro}`, "i");
            if (macroRegex.test(line)) {
              vectorHits.push({ macro: vm.macro, isa: vm.isa, file: relPath, line: i + 1 });
            }
          }

          for (const pm of PLATFORM_MACROS) {
            const macroRegex = new RegExp(`#ifdef\\s+${pm.macro}|#if\\s+defined\\s*\\(\\s*${pm.macro}\\s*\\)|#if\\s+.*${pm.macro}`, "i");
            if (macroRegex.test(line)) {
              platformHits.push({ macro: pm.macro, platform: pm.platform, file: relPath, line: i + 1 });
            }
          }

          for (const ip of INTRINSIC_PATTERNS) {
            if (line.includes(ip.pattern) && !line.trim().startsWith("//") && !line.trim().startsWith("/*")) {
              intrinsicHits.push({ pattern: ip.pattern, isa: ip.isa, file: relPath, line: i + 1 });
            }
          }
        }
      } catch {
        // skip unreadable files
      }
    }

    results.push(`=== Architecture Macros (${archHits.length} found) ===`);
    if (archHits.length > 0) {
      const grouped = new Map<string, typeof archHits>();
      for (const h of archHits) {
        if (!grouped.has(h.arch)) grouped.set(h.arch, []);
        grouped.get(h.arch)!.push(h);
      }
      for (const [arch, hits] of grouped) {
        results.push(`  ${arch}: ${hits.length} occurrence(s)`);
        for (const h of hits.slice(0, 10)) {
          results.push(`    ${h.file}:${h.line} (${h.macro})`);
        }
        if (hits.length > 10) {
          results.push(`    ... and ${hits.length - 10} more`);
        }
      }
    } else {
      results.push("  (none found — no explicit architecture guards)");
    }
    results.push("");

    results.push(`=== Vectorization Macros (${vectorHits.length} found) ===`);
    if (vectorHits.length > 0) {
      const grouped = new Map<string, typeof vectorHits>();
      for (const h of vectorHits) {
        if (!grouped.has(h.isa)) grouped.set(h.isa, []);
        grouped.get(h.isa)!.push(h);
      }
      for (const [isa, hits] of grouped) {
        results.push(`  ${isa}: ${hits.length} occurrence(s)`);
        for (const h of hits.slice(0, 10)) {
          results.push(`    ${h.file}:${h.line} (${h.macro})`);
        }
        if (hits.length > 10) {
          results.push(`    ... and ${hits.length - 10} more`);
        }
      }
    } else {
      results.push("  (none found)");
    }
    results.push("");

    results.push(`=== Platform Macros (${platformHits.length} found) ===`);
    if (platformHits.length > 0) {
      const grouped = new Map<string, typeof platformHits>();
      for (const h of platformHits) {
        if (!grouped.has(h.platform)) grouped.set(h.platform, []);
        grouped.get(h.platform)!.push(h);
      }
      for (const [platform, hits] of grouped) {
        results.push(`  ${platform}: ${hits.length} occurrence(s)`);
        for (const h of hits.slice(0, 10)) {
          results.push(`    ${h.file}:${h.line} (${h.macro})`);
        }
        if (hits.length > 10) {
          results.push(`    ... and ${hits.length - 10} more`);
        }
      }
    } else {
      results.push("  (none found — no explicit platform guards)");
    }
    results.push("");

    results.push(`=== Intrinsic Usage (${intrinsicHits.length} found) ===`);
    if (intrinsicHits.length > 0) {
      const grouped = new Map<string, typeof intrinsicHits>();
      for (const h of intrinsicHits) {
        if (!grouped.has(h.isa)) grouped.set(h.isa, []);
        grouped.get(h.isa)!.push(h);
      }
      for (const [isa, hits] of grouped) {
        results.push(`  ${isa}: ${hits.length} occurrence(s)`);
        for (const h of hits.slice(0, 10)) {
          results.push(`    ${h.file}:${h.line} (pattern: ${h.pattern})`);
        }
        if (hits.length > 10) {
          results.push(`    ... and ${hits.length - 10} more`);
        }
      }
    } else {
      results.push("  (none found — no vector intrinsic calls)");
    }

    return results.join("\n");
  },
});