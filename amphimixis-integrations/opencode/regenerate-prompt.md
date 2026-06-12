# Agent Regeneration Instructions

Use these instructions when `docs/methodology.md` has been updated and the opencode agent definitions in `integrations/opencode/agents/` need to be regenerated or updated to match.

## Step 1: Determine Regeneration Scope

Read the following files completely:
1. `docs/methodology.md` (the updated version)
2. `integrations/opencode/agents/amphimixis-orchestrator.md`
3. `integrations/opencode/agents/amphimixis-repo-check.md`
4. `integrations/opencode/agents/amphimixis-build.md`
5. `integrations/opencode/agents/amphimixis-profiler.md`
6. `integrations/opencode/agents/amphimixis-optimizer.md`
7. `AGENTS.md`
8. `docs/report-template.md`

### Analysis Questions

Answer these questions by comparing the methodology to the agent definitions:

| Question | How to answer |
|----------|---------------|
| Did a NEW step get added to the methodology? | Compare step count in methodology vs agent structure |
| Did an EXISTING step change its procedure? | Check if tool calls, flags, or order changed |
| Did a tool name/parameter change? | Check `integrations/opencode/tools/*.ts` for any changes (tools should NOT change, but verify) |
| Did the report format change? | Compare `docs/report-template.md` against each agent's reporting section |
| Did the frontmatter requirements change? | Check if opencode updated its agent schema (rare) |

### Decision

- **Full regeneration** if: methodology has new steps that cannot be fully implemented in the old version (changes to other steps are required) or steps reordered.
- **Partial regeneration** if: only specific steps changed (e.g., profiling methodology changed → regenerate only `amphimixis-profiler.md`).
- **No regeneration needed** if: changes are editorial (wording, clarifications, examples) and do not affect agent behavior.

Output your decision clearly: `DECISION: [Full | Partial: <affected agents> | None]`

## Step 2: Regenerate Each Affected Agent

For each agent that needs regeneration:

### 2a. Read the Current Agent

Read the current `.md` file from `integrations/opencode/agents/`.

### 2b. Map Methodology Steps to Agent Actions

For each step in the methodology, map it to a tool call:

```
Methodology: "Build project with -O3 -march=native -g"
→ Agent action: Call `build-with-flags` with {optLevel: "-O3", march: "-march=native", debug: "-g"}
```

Rules:
- Every methodology procedure must map to at least one tool call or subagent delegation.
- If a methodology step has NO corresponding tool, the agent should use `bash` with explicit commands.
- If the methodology describes a verification step, the agent must include a self-check after the corresponding action.

### 2c. Write the Frontmatter (Opencode agents documentation accordingly (read in Network)) 

For example

```yaml
---
description: <one-line description of what this agent does>
mode: <subagent | all | primary>
temperature: 0.2
color: "<hex color>"
permission:
  <tool name>: <allow | deny>
  bash:
    "<command pattern>": <allow | deny>
  task:
    "<subagent pattern>": <allow | deny>
---
```

### 2d. Self-Check After Writing

Verify ALL of these before considering the agent complete:

| # | Check | Pass/Fail |
|---|-------|-----------|
| 1 | Frontmatter `description` is present and accurate | |
| 2 | Frontmatter `mode` is correct (`subagent` for worker agents, `all` for orchestrator) | |
| 3 | Frontmatter `permission` allows all tools the agent needs to call | |
| 4 | Frontmatter `permission.task` allows all subagents the agent delegates to | |
| 5 | The agent only calls tools listed in `integrations/opencode/tools/*.ts` or built-in opencode tools | |
| 6 | Every tool call includes all required parameters | |
| 7 | Every critical step has a self-check section after it | |
| 8 | The agent uses `task` for subagent delegation, NOT `@mention` or `bash` | |
| 9 | The report format sections match `docs/report-template.md` | |
| 10 | No assumptions without data — every claim requires tool output | |
| 11 | Causal analysis required: "why" not just "what" | |

If any check fails, fix the agent file before proceeding.

## Step 3: Update AGENTS.md (if needed)

If the methodology change introduces new conventions, commands, or rules, update `AGENTS.md` accordingly.

## Step 4: Sync and Verify

After all agent files are written:

1. **Verify CI would pass**: Check that no methodology-only commits exist without corresponding agent changes.

## Summary Checklist

- [ ] Step 1: Regeneration scope determined (full / partial / none)
- [ ] Step 2: All affected agents regenerated
- [ ] Step 3: Self-checks passed for each agent
- [ ] Step 4: AGENTS.md updated if needed
- [ ] Step 5: Files synced to deployment location
- [ ] Step 6: Everything committed together
