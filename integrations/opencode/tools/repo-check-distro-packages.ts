import { tool } from "@opencode-ai/plugin";

export default tool({
  description: `Check if a project exists as a package in major Linux distributions (Debian, Arch, Yocto)
and retrieve any distribution-specific patches.

RULES:
- projectName is REQUIRED — the name of the project/package to look up.
- Checks Debian packages site, Arch AUR, and Yocto layer index via web fetch.
- Returns package availability, version, and patch information.

EXAMPLES:
  {projectName: 'yaml-cpp'}
  {projectName: 'rapidxml'}`,
  args: {
    projectName: tool.schema
      .string()
      .describe("Name of the project/package to look up"),
  },
  async execute(args) {
    const name = args.projectName.trim().toLowerCase();
    const results: string[] = [];
    results.push(`Distribution package check for: ${args.projectName}`);
    results.push("");

    // Debian
    results.push("=== Debian ===");
    try {
      const debianResp = await fetch(
        `https://packages.debian.org/search?keywords=${encodeURIComponent(name)}&searchon=names&suite=all&section=all`,
      );
      const debianText = await debianResp.text();
      if (debianText.includes("No packages found")) {
        results.push("  Status: NOT FOUND in Debian repositories");
      } else {
        const match = debianText.match(
          /<a href="\/[a-z]+\/[a-z]+\/[a-zA-Z0-9_.-]+">([a-zA-Z0-9_.-]+)<\/a>/,
        );
        if (match) {
          results.push(`  Status: FOUND as package "${match[1]}"`);
          const count = (debianText.match(/class="package"/g) || []).length;
          results.push(`  Packages found: ${count}`);
        } else {
          results.push("  Status: Possible match (check manually)");
        }
      }
    } catch (e) {
      results.push(`  Error checking Debian: ${e}`);
    }
    results.push("");

    // Arch AUR
    results.push("=== Arch Linux (AUR) ===");
    try {
      const aurUrl = `https://aur.archlinux.org/rpc/v2/info?arg[]=${encodeURIComponent(name)}`;
      const aurResp = await fetch(aurUrl);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const aurData: any = await aurResp.json();
      if (aurData.resultcount > 0) {
        const pkg = aurData.results[0];
        results.push(`  Status: FOUND`);
        results.push(`  Package: ${pkg.Name}`);
        results.push(`  Version: ${pkg.Version}`);
        results.push(`  Description: ${pkg.Description}`);
        results.push(`  URL: https://aur.archlinux.org/packages/${pkg.Name}`);
      } else {
        results.push("  Status: NOT FOUND in AUR");
      }
    } catch (e) {
      results.push(`  Error checking AUR: ${e}`);
    }
    results.push("");

    // Yocto / OpenEmbedded
    results.push("=== Yocto / OpenEmbedded ===");
    try {
      const yoctoResp = await fetch(
        `https://layers.openembedded.org/layerindex/api/recipes/?search=${encodeURIComponent(name)}`,
      );
      const yoctoText = await yoctoResp.text();
      let yoctoData;
      try {
        yoctoData = JSON.parse(yoctoText);
      } catch {
        yoctoData = null;
      }
      if (yoctoData && yoctoData.count > 0) {
        results.push(`  Status: FOUND (${yoctoData.count} recipe(s))`);
        for (let i = 0; i < Math.min(yoctoData.results.length, 5); i++) {
          const r = yoctoData.results[i];
          results.push(`  - ${r.pn || r.name} (${r.layerbranch?.layer?.name || "unknown"})`);
        }
      } else {
        results.push("  Status: NOT FOUND in OpenEmbedded layer index");
      }
    } catch (e) {
      results.push(`  Error checking Yocto: ${e}`);
    }
    results.push("");

    results.push("NOTE: For comprehensive patch information, check distro-specific source package repos.");
    return results.join("\n");
  },
});