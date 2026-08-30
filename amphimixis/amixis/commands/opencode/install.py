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

    src_root = project_root / "amphimixis-integrations" / "opencode"
    src_general = project_root / "amphimixis-integrations" / "inspector_general.ts"

    print(f"Installing methodology agents and tools to {config_dir}")

    install_sources = [
        (src_root / "agents", "*.md", config_dir / "agents", "agents"),
        (src_root / "tools", "*.ts", config_dir / "tools", "tools"),
        (src_root / "commands", "*.md", config_dir / "commands", "commands"),
        (src_root / "plugins", "*.ts", config_dir / "plugins", "plugins"),
    ]

    for src_dir, pattern, dst_dir, label in install_sources:
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in src_dir.glob(pattern):
            shutil.copy2(f, dst_dir)
            count += 1
        print(f"  Copied {count} {label}")

    if src_general.exists():
        dst_general = config_dir / "node_modules" / "inspector_general.ts"
        dst_general.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_general, dst_general)
        print("  Copied inspector_general to {Opencode config dir}/node_modules/")

    print("  Installing Bun dependencies...")
    if shutil.which("bun") is not None:
        subprocess.run(
            [
                "bun",
                "install",
                "yaml",
                "async-mutex",
                "unified",
                "remark-parse",
                "remark-gfm",
            ],
            cwd=config_dir,
            check=False,
        )
    else:
        print("    bun not found — install it from https://bun.sh")

    print()
    print("Installation complete!")
    print("  Agents:  ", len(list((config_dir / "agents").glob("*.md"))))
    print("  Tools:   ", len(list((config_dir / "tools").glob("*.ts"))))
    print("  Commands:", len(list((config_dir / "commands").glob("*.md"))))
    print("  Plugins: ", len(list((config_dir / "plugins").glob("*.ts"))))
    print()
    print("Methodology agents and tools are now available in opencode.")

    return True


def get_opencode_config_dir_path(is_global: bool = False) -> Path:
    """Give path to Opencode configuration directory.

    :param bool is_global: If True then give path
        to global directory otherwise local directory.
    """
    if is_global:
        config_dir = (
            Path(environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser().resolve()
        )
        return config_dir / "opencode"

    return Path(".").resolve() / ".opencode"
