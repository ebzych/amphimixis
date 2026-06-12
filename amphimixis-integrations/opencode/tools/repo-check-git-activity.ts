import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

export default tool({
  description: `Check git activity of a repository: latest commits, tags, branches, and release history.

RULES:
- repoPath is REQUIRED and must point to an existing git repository.
- Runs 'git log --oneline -20', 'git tag --list', 'git branch -a', 'git remote -v'.
- Returns formatted summary of repository activity.

EXAMPLES:
  {repoPath: '/home/user/project'}
  {repoPath: '.'}`,
  args: {
    repoPath: tool.schema
      .string()
      .describe("Path to the git repository to inspect"),
  },
  async execute(args) {
    const repoPath = path.resolve(args.repoPath);

    if (!fs.existsSync(repoPath)) {
      return `Error: Path does not exist: ${repoPath}`;
    }

    const gitDir = path.join(repoPath, ".git");
    if (!fs.existsSync(gitDir)) {
      return `Error: Not a git repository: ${repoPath}`;
    }

    const results: string[] = [];
    results.push(`Repository: ${repoPath}`);
    results.push("");

    try {
      const logOutput = await Bun.$`git -C ${repoPath} log --oneline -20`.text();
      results.push("=== Recent Commits (last 20) ===");
      results.push(logOutput.trim());
    } catch {
      results.push("=== Recent Commits === (no commits found)");
    }
    results.push("");

    try {
      const tagOutput = await Bun.$`git -C ${repoPath} tag --list`.text();
      const tags = tagOutput.trim().split("\n").filter(Boolean);
      results.push(`=== Tags (${tags.length} found) ===`);
      if (tags.length > 0) {
        results.push(tags.join("\n"));
      } else {
        results.push("(no tags)");
      }
    } catch {
      results.push("=== Tags === (error reading tags)");
    }
    results.push("");

    try {
      const branchOutput = await Bun.$`git -C ${repoPath} branch -a`.text();
      const branches = branchOutput.trim().split("\n").filter(Boolean);
      results.push(`=== Branches (${branches.length} found) ===`);
      results.push(branches.join("\n"));
    } catch {
      results.push("=== Branches === (error reading branches)");
    }
    results.push("");

    try {
      const remoteOutput = await Bun.$`git -C ${repoPath} remote -v`.text();
      const remotes = remoteOutput.trim().split("\n").filter(Boolean);
      results.push(`=== Remotes (${remotes.length} found) ===`);
      if (remotes.length > 0) {
        results.push(remotes.join("\n"));
      } else {
        results.push("(no remotes configured)");
      }
    } catch {
      results.push("=== Remotes === (error reading remotes)");
    }

    return results.join("\n");
  },
});