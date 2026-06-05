"""Opencode install subcommand."""

import shutil
import subprocess
from os import environ
from pathlib import Path


def run_opencode_install(globally: bool = False) -> bool:
    """Install methodology agents and tools into Opencode config directory.

    :param bool globally: If True install globally (XDG_CONFIG_HOME/opencode),
        otherwise locally (.opencode in current directory)
    :return: True if installation succeeded, False otherwise
    :rtype: bool
    """
    self_path = Path(__file__).parent.resolve()
    project_root = self_path.parent.parent.parent.parent.resolve()
    config_dir = get_opencode_config_dir_path(is_global=globally)
    agents_dir = config_dir / "agents"
    tools_dir = config_dir / "tools"

    print(f"Installing methodology agents and tools to {config_dir}")

    agents_dir.mkdir(parents=True, exist_ok=True)
    tools_dir.mkdir(parents=True, exist_ok=True)

    methodology_agents = project_root / "integrations" / "opencode" / "agents"
    methodology_tools = project_root / "integrations" / "opencode" / "tools"
    amphimixis_agents = project_root / "opencode" / "agents"
    amphimixis_tools = project_root / "opencode" / "tools"

    print("  Copying methodology agents...")
    for f in methodology_agents.glob("*.md"):
        shutil.copy2(f, agents_dir)

    print("  Copying methodology tools...")
    for f in methodology_tools.glob("*.ts"):
        shutil.copy2(f, tools_dir)

    if amphimixis_agents.is_dir():
        print("  Copying amphimixis agents...")
        for f in amphimixis_agents.glob("*.md"):
            shutil.copy2(f, agents_dir)

    if amphimixis_tools.is_dir():
        print("  Copying amphimixis tools...")
        for f in amphimixis_tools.glob("*.ts"):
            shutil.copy2(f, tools_dir)

    print("  Installing bun dependencies...")
    if shutil.which("bun") is not None:
        subprocess.run(
            ["bun", "install", "yaml"],
            cwd=config_dir,
            check=False,
        )
    else:
        print("    bun not found — install it from https://bun.sh")

    agent_count = len(list(agents_dir.glob("*.md")))
    tool_count = len(list(tools_dir.glob("*.ts")))

    print()
    print("Installation complete!")
    print(f"  Agents installed: {agent_count}")
    print(f"  Tools installed: {tool_count}")
    print()
    print("Methodology agents and tools are now available in opencode.")

    return True


def get_opencode_config_dir_path(is_global: bool = False) -> Path:
    """Give path to Opencode configuration directory.

    :param bool is_global: If True then give path
        to global directory otherwise local directory.
    """
    if is_global:
        config_dir = Path(environ.get("XDG_CONFIG_HOME", "~/.config")).resolve()
        return config_dir / "opencode"

    return Path(".").resolve() / ".opencode"
