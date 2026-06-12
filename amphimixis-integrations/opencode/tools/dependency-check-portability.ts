import { tool } from "@opencode-ai/plugin";

interface PortabilityRecord {
  name: string;
  status: "ready" | "partial" | "unknown" | "missing";
  architectures: string[];
  notes?: string;
}

const DEFAULT_DATABASE: PortabilityRecord[] = [
  {
    name: "yaml-cpp",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Well-ported; CMake-based, no arch-specific code.",
  },
  {
    name: "rapidxml",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Header-only, no arch-specific code.",
  },
  {
    name: "boost",
    status: "partial",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Most libraries are portable; some components (e.g., context, atomic) need arch-specific assembly.",
  },
  {
    name: "openssl",
    status: "partial",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Has arch-specific optimized code; RISC-V support improving.",
  },
  {
    name: "zlib",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Fully portable, no arch-specific intrinsics by default.",
  },
  {
    name: "libpng",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Portable, with optional optimizations for different architectures.",
  },
  {
    name: "libjpeg-turbo",
    status: "partial",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Has SIMD optimizations for x86, ARM; RISC-V SIMD support pending.",
  },
  {
    name: "fmt",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Header-only or compiled; no arch-specific code.",
  },
  {
    name: "spdlog",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Header-only logging library; no arch-specific code.",
  },
  {
    name: "nlohmann-json",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Header-only JSON library; completely portable.",
  },
  {
    name: "catch2",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Header-only testing framework; fully portable.",
  },
  {
    name: "gtest",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Google Test; fully portable.",
  },
  {
    name: "pthread",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "POSIX threads; available on all Linux platforms.",
  },
  {
    name: "curl",
    status: "ready",
    architectures: ["x86", "x86_64", "arm", "aarch64", "riscv64"],
    notes: "Portable; minimal arch-specific code.",
  },
];

function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[-_]/g, "")
    .replace(/lib/, "");
}

export default tool({
  description: `Check the portability status of a project dependency for a target architecture.

Queries an internal portability database to determine if a dependency is ready, partially ready,
unknown, or missing for the specified architecture.

RULES:
- dependencyName: REQUIRED. Name of the dependency to check.
- targetArch: REQUIRED. Target architecture (e.g., 'x86', 'riscv64', 'aarch64', 'arm').
- If dependency is not in database, marks as 'missing' and reports the gap.

EXAMPLES:
  {dependencyName: 'yaml-cpp', targetArch: 'riscv64'}
  {dependencyName: 'openssl', targetArch: 'aarch64'}`,
  args: {
    dependencyName: tool.schema
      .string()
      .describe("Name of the dependency to check"),
    targetArch: tool.schema
      .string()
      .describe("Target architecture to check against (e.g., x86, riscv64, aarch64, arm)"),
  },
  async execute(args) {
    const depName = args.dependencyName.trim();
    const arch = args.targetArch.trim().toLowerCase();

    const results: string[] = [];
    results.push(`Portability check: ${depName} → ${arch}`);
    results.push("");

    const normalized = normalizeName(depName);
    let record: PortabilityRecord | undefined;

    for (const r of DEFAULT_DATABASE) {
      if (normalizeName(r.name) === normalized) {
        record = r;
        break;
      }
    }

    if (!record) {
      results.push("  Status: MISSING from portability database");
      results.push(`  Dependency "${depName}" has not been evaluated for portability.`);
      results.push("");
      results.push("  ACTION REQUIRED:");
      results.push("  - Evaluate the portability of this dependency manually.");
      results.push("  - Add the result to the portability database and report.");
      return results.join("\n");
    }

    const archSupported = record.architectures.some((a) => a === arch || a.startsWith(arch));

    results.push(`  Status: ${record.status.toUpperCase()}`);
    results.push(`  Supported architectures: ${record.architectures.join(", ")}`);
    results.push(`  Target arch (${arch}) supported: ${archSupported ? "YES" : "NO"}`);
    if (record.notes) {
      results.push(`  Notes: ${record.notes}`);
    }

    if (!archSupported) {
      results.push("");
      results.push("  WARNING: This dependency may not be fully portable to the target architecture.");
      results.push("  Further investigation and testing required.");
    }

    return results.join("\n");
  },
});