import { tool } from "@opencode-ai/plugin";
import fs from "fs";
import path from "path";

const README_PATTERNS = [
  "README.md", "README.rst", "README.txt", "README",
  "readme.md", "readme.rst", "readme.txt",
];

export default tool({
  description: `Parse README files of a project to find references to repository moves,
upstream parent projects, or migration to larger projects (e.g., RapidXML moved to Boost).

RULES:
- repoPath is REQUIRED.
- Searches common README filenames.
- Looks for URLs, "moved to", "see also", "superseded by" patterns.
- Returns extracted references and links.

EXAMPLES:
  {repoPath: '/home/user/project'}`,
  args: {
    repoPath: tool.schema
      .string()
      .describe("Path to the repository to inspect"),
  },
  async execute(args) {
    const repoPath = path.resolve(args.repoPath);

    if (!fs.existsSync(repoPath)) {
      return `Error: Path does not exist: ${repoPath}`;
    }

    const results: string[] = [];
    results.push(`Scanning README files in: ${repoPath}`);
    results.push("");

    let foundAny = false;

    for (const pattern of README_PATTERNS) {
      const readmePath = path.join(repoPath, pattern);
      if (fs.existsSync(readmePath)) {
        foundAny = true;
        results.push(`=== Found: ${pattern} ===`);
        const content = fs.readFileSync(readmePath, { encoding: "utf-8" });
        const lines = content.split("\n");

        const moveKeywords = [
          "moved to", "moved", "superseded", "deprecated",
          "see also", "part of", "incorporated", "redirect",
          "upstream", "originally", "formerly",
        ];
        const urlPattern = /https?:\/\/[^\s)\]}]+/g;

        const relevantLines: { line: number; text: string }[] = [];
        const urls: string[] = [];

        for (let i = 0; i < lines.length; i++) {
          const lineLower = lines[i].toLowerCase();
          const hasKeyword = moveKeywords.some((kw) => lineLower.includes(kw));
          if (hasKeyword) {
            relevantLines.push({ line: i + 1, text: lines[i].trim() });
          }

          const foundUrls = lines[i].match(urlPattern);
          if (foundUrls) {
            urls.push(...foundUrls);
          }
        }

        if (relevantLines.length > 0) {
          results.push("--- Lines mentioning moves/redirects ---");
          for (const rl of relevantLines) {
            results.push(`  L${rl.line}: ${rl.text}`);
          }
        } else {
          results.push("(no move/redirect references found)");
        }

        if (urls.length > 0) {
          results.push("--- URLs found in README ---");
          const uniqueUrls = [...new Set(urls)];
          for (const u of uniqueUrls) {
            results.push(`  ${u}`);
          }
        }

        results.push("");
      }
    }

    if (!foundAny) {
      results.push("(no README file found)");
    }

    return results.join("\n");
  },
});