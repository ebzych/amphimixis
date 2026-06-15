# Amphimixis Opencode integration

This directory contains Opencode agents and tools for integrating Amphimixis with LLM-chat --- a multi-agent system that automates migration-readiness analysis of software projects.

## Table of Contents

- [Directory structure](#directory-structure)
- [Agent lifecycle](#agent-lifecycle)
- [Regeneration pipeline](#regeneration-pipeline)
- [When to regenerate](#when-to-regenerate)
- [Agents reference](#agents-reference)

---

## Directory structure

```
amphimixis-integrations/opencode/
├── README.md           ← this file
├── agents/             ← agent definitions
│   ├── amphimixis.md              orchestrator
│   ├── amphimixis-analyzer.md     repository analyser
│   ├── amphimixis-configurator.md config writer
│   ├── amphimixis-builder.md      build & test runner
│   ├── amphimixis-profiler.md     performance profiler
│   └── amphimixis-optimizer.md    optimisation recommender
├── tools/              ← TypeScript wrappers under which the `amixis` works and other tools
│   ├── amphimixis-analyze.ts
│   ├── amphimixis-analyze-vectorization.ts
│   ├── amphimixis-build.ts
│   ├── amphimixis-configure-platforms.ts
│   ├── amphimixis-configure-recipes.ts
│   ├── amphimixis-configure-builds.ts
│   ├── amphimixis-profile.ts
│   └── amphimixis-validate.ts
└── __tests__/          ← LLM-tools tests
    ├── analyzing_test.ts
    ├── building_test.ts
    ├── configuring_test.ts
    ├── profiling_test.ts
    └── validating_test.ts
```

The agents are installed into Opencode via `amixis opencode install` (see [docs/opencode_agent.md](../../docs/opencode_agent.md)).

---

## Agent lifecycle

The agent definitions in `agents/` are **generated artefacts**. They are derived from the methodology document at `docs/methodologies/migration-readiness-exploring-methodology.md`, which is the single source of truth for how the agents should behave.

>Methodology (source) -> Agent definitions (agents/*.md)

When the methodology changes, the agents must be regenerated to stay in sync.

---

## Regeneration pipeline

### Staff
- `agents-regenerator` --- `.opencode/agents/agents-regenerator.md` --- knows how to regenerate agents
- `migration-expert` --- `.opencode/agents/migration-expert.md` --- assesses the report from the generated agent (to improve generated agents)

### Pipeline

Regeneration is triggered manually by calling the `agents-regenerator` agent:

   1. Methodology updated.

   2. `agents-regenerator`
       with prompt "Methodology has been updated —
       regenerate agents?"

      Reads methodology + current agents,
      compares, decides scope:
        FULL / PARTIAL (\<agents\>) / NONE.

   3. `amphimixis` (orchestrator)
      with prompt "Analyze TinyXML2 project for migration to RISC-V readiness"
 
      Produces a migration-readiness report.

   4. `migration-expert`
      with prompt "Assess the report"

      Evaluates report against methodology:
      quality, completeness, correctness, experimental rigour.

   5. agents-regenerator (feedback loop)
      "Improvements from expert:
       \<assessment\>"

      Incorporates expert feedback, refines agent definitions, re-runs self-checks.

### Stage details

#### 1. Trigger

The methodology has been updated (e.g. a new step added, an existing procedure changed, the report template modified).

#### 2. Decision (`agents-regenerator`)

The regenerator reads the updated methodology and all current agent definitions. It compares the methodology steps against what the agents implement and answers:

| Question | How to answer |
|----------|---------------|
| Did a NEW step get added? | Compare step count in methodology vs agent structure |
| Did an EXISTING step change? | Check if tool calls, flags, or order changed |
| Did the report format change? | Compare `docs/methodologies/report-template.md` against each agent's reporting section |
| Did the frontmatter requirements change? | Check if opencode updated its agent schema |

Output is one of:
- `DECISION: Full` — regenerate all agents
- `DECISION: Partial: <agent list>` — regenerate specific agents only
- `DECISION: None` — no changes needed

#### 3. Generation test (`amphimixis` orchestrator)

On a FULL or PARTIAL decision the regenerator generates (or updates) the agent files. Then should **validate them** by running the full pipeline through the `amphimixis` orchestrator on a representative test project (TinyXML2). This produces a migration-readiness report, exercising all subagents.

#### 4. Expert review (`migration-expert`)

The generated report is passed to `migration-expert`, which evaluates it with an extra thought:

- Is there unnecessary duplication?
- Is the analysis too superficial?
- Is the experiment pure and reproducible?
- Does the methodology experiment work as designed?
- Does the report match the template?
- Is the result useful for professional migration decisions?

#### 5. Improvement loop (`agents-regenerator`)

The expert assessment is fed back into the `agents-regenerator`, which refines the agent definitions to fix any issues found. This loop repeats until the expert is satisfied (self-checks pass).

---

## When to regenerate

| Trigger | Required action |
|---------|-----------------|
| New step added to methodology | FULL regeneration |
| Existing step procedure changed | PARTIAL — regenerate affected agents |
| Report template updated | PARTIAL — regenerate agents that produce reports |
| Tool interface changed (rare) | PARTIAL — regenerate agents that use the tool |
| Editorial changes only (wording, clarifications) | NONE — skip regeneration |

---

## Agents reference

| Agent | File | Role | Delegates to / Uses |
|-------|------|------|---------------------|
| `amphimixis` (orchestrator) | `agents/amphimixis.md` | Coordinates the full pipeline; compiles final report | All subagents |
| `amphimixis-analyzer` | `agents/amphimixis-analyzer.md` | Clone repo, scan macros/intrinsics, assess deps | `amphimixis-analyze` tool |
| `amphimixis-configurator` | `agents/amphimixis-configurator.md` | Create `input.yml` (platforms → recipes → builds) | configure-* tools, validate tool |
| `amphimixis-builder` | `agents/amphimixis-builder.md` | Build on reference + target, run tests | `amphimixis-build` tool |
| `amphimixis-profiler` | `agents/amphimixis-profiler.md` | Profile executables, cross-table comparison | `amphimixis-profile`, `amphimixis-analyze-vectorization` |
| `amphimixis-optimizer` | `agents/amphimixis-optimizer.md` | Analyse bottlenecks, suggest optimisations | `amphimixis-analyze-vectorization` |
