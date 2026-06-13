"""Opencode install subcommand."""

import shutil
import subprocess
from inspect import stack
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
    agents_dst = config_dir / "agents"
    tools_dst = config_dir / "tools"

    print(f"Installing methodology agents and tools to {config_dir}")

    agents_dst.mkdir(parents=True, exist_ok=True)
    tools_dst.mkdir(parents=True, exist_ok=True)

    agents_src = project_root / "amphimixis-integrations" / "opencode" / "agents"
    tools_src = project_root / "amphimixis-integrations" / "opencode" / "tools"
    print(agents_src, tools_src, agents_dst, tools_dst)

    print("  Copying Amphimixis agents...")
    for f in agents_src.glob("*.md"):
        shutil.copy2(f, agents_dst)

    print("  Copying Amphimixis tools...")
    for f in tools_src.glob("*.ts"):
        shutil.copy2(f, tools_dst)

    # amixis script should be executed first
    amixis_executable_path = Path(stack()[-1].filename).resolve().__str__()
    for root, _, files in tools_dst.walk():
        for file in files:
            if '.ts' in file:
                path = Path(root) / file
                content: str
                with open(path, "r") as f:
                    content = f.read() 
                content = content.replace(
                    "__TEMPLATE_STRING_FOR_PATH_TO_AMIXIS_TO_BE_INSERTED_AT_INSTALLATION__",
                    amixis_executable_path,
                    1
                    )
                with open(path, "w") as f:
                    f.write(content)

    print("  Installing Bun dependencies...")
    if shutil.which("bun") is not None:
        subprocess.run(
            ["bun", "install", "yaml"],
            cwd=config_dir,
            check=False,
        )
    else:
        print("    bun not found — install it from https://bun.sh")

    agent_count = len(list(agents_dst.glob("*.md")))
    tool_count = len(list(tools_dst.glob("*.ts")))

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
