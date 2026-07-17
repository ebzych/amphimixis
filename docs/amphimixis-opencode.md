# Amphimixis-Opencode — an LLM-powered assistant that automates the full migration-readiness analysis pipeline

## About

Amphimixis-Opencode helps you analyze your project for migration ability --- __it automates this process__. It provides an agent system and formal tools for Opencode:

- `Amphimixis` --- orchestrator agent, and subagents which calling by orchestrator
- Tools --- wrappers around the `amixis` CLI and other tools

---

## Table of Contents

- [Usage](#usage)
- [Pipeline](#pipeline)
- [Tool reference](#tool-reference)
- [Installation](#installation)
- [Running the tests](#running-the-tests)

---

## Usage

```bash
amixis opencode run "<your prompt>"
```

The prompt should describe the project and task. For example:

```bash
amixis opencode run "Analyse the <Name> project, identify platform-specific code, and produce a migration report for RISC-V. Use my cross-toolchain /path/to/toolchain."
```

This opens the Opencode TUI with `amphimixis` agent and your prompt.

> **Note:** The agent expects the current working directory to contain (or point to) the project being analysed. Use an absolute path in the prompt for clarity.

---

## Pipeline

When invoked, `amphimixis` runs a 7-phase pipeline:

| Phase                  | Subagent                  | Description                                                                                         |
|------------------------|---------------------------|-----------------------------------------------------------------------------------------------------|
| 1. Repository analysis | `amphimixis-analyzer`     | Find actual repo, clone it, scan for platform-specific macros and intrinsics, assess dependencies   |
| 2. Configuration       | `amphimixis-configurator` | Create the `input.yml` (see [Usage Guide](usage_guide.md)) file with platforms, recipes, and builds |
| 3. Build & verify      | `amphimixis-builder`      | Build on reference and target platforms, run tests                                                  |
| 4. Profiling           | `amphimixis-profiler`     | Profile executables, produce a cross-platform comparison                                            |
| 5. Optimization        | `amphimixis-optimizer`    | Analyse bottlenecks and suggest improvements                                                        |
| 6. Repeat pipeline     | `amphimixis`              | Apply optimizations, rebuild, re-profile, compare before/after                                      |
| 7. Final report        | `amphimixis`              | Compile a structured report by the [Report Template](methodologies/report-template.md)              |

The agent hierarchy follows a strict delegation pattern:

```
amphimixis (orchestrator)   mode: all
│   delegates work, never calls tools directly
│
├── amphimixis-analyzer     mode: subagent
│   └── uses: amphimixis-analyze.ts, amphimixis-analyze-vectorization.ts
│
├── amphimixis-configurator mode: subagent
│   └── uses: amphimixis-configure-platforms.ts,
│             amphimixis-configure-recipes.ts,
│             amphimixis-configure-builds.ts,
│             amphimixis-validate.ts
│
├── amphimixis-builder      mode: subagent
│   └── uses: amphimixis-build.ts
│
├── amphimixis-profiler     mode: subagent
│   └── uses: amphimixis-profile.ts,
│             amphimixis-analyze-vectorization.ts
│
└── amphimixis-optimizer    mode: subagent
    └── uses: amphimixis-analyze-vectorization.ts
```

Each subagent receives structured context from its predecessor and passes results forward. The orchestrator validates completeness after each phase before proceeding.

---

## Tool reference

All tools are defined as TypeScript files using `@opencode-ai/plugin`.

| Tool                                  | Action                                                     | Purpose |
|---------------------------------------|------------------------------------------------------------|---------|
| `amphimixis-analyze.ts`               | Run `amixis analyze <path>`                                | Detect build systems, test frameworks, CI, documentation, dependencies |
| `amphimixis-analyze-vectorization.ts` | Run `amixis analyze -v <arch> <binary>`                    | Scan a binary for platform-specific vector instructions (SSE, AVX, AVX-512, NEON, RVV) |
| `amphimixis-build.ts`                 | Run `amixis build <path> [--config] [--build-name]`        | Build the project using a specific configuration |
| `amphimixis-configure-platforms.ts`   | Add platforms to `platforms` field in `amixis` config file | Add machine definitions to `input.yml` with auto-assigned IDs |
| `amphimixis-configure-recipes.ts`     | Add recipes to `recipes` field in `amixis` config file     | Add build recipes (flags, toolchain, sysroot) to `input.yml` |
| `amphimixis-configure-builds.ts`      | Add builds to `builds` field in `amixis` config file       | Link platforms and recipes into executable build tasks |
| `amphimixis-profile.ts`               | Run `amixis profile <path> [--config] [--build-name]`      | Profile executables with `perf stat` and `perf record` |
| `amphimixis-validate.ts`              | Run `amixis validate <config>`                             | Validate an `input.yml` configuration file |

The configure tools write YAML directly rather than calling the CLI — they manipulate `input.yml` programmatically.

---

## Installation

### Requirements

- A working `amixis` installation (see [Usage Guide](usage_guide.md#choose-an-installation-method))
- The Opencode CLI (`opencode`) installed and available on `PATH`
- `bun` for installing test/utility dependencies

### Install the agents and tools

```bash
amixis opencode install
```

This copies agents and tools into the local `.opencode/` directory.

For a system-wide installation, pass the `--global` flag:

```bash
amixis opencode install --global
```

This installs the agents and tools into `$XDG_CONFIG_HOME/opencode` (defaults to `~/.config/opencode`).

---

## Running the tests

Tests use **Bun's built-in test runner** (`bun:test`). They reside in `amphimixis-integrations/opencode/__tests__/`.

```bash
cd amphimixis-integrations/opencode
bun test
```
