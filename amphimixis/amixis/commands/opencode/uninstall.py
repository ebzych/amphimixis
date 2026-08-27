"""Opencode uninstall subcommand."""

from pathlib import Path

from amphimixis.amixis.commands.opencode.install import (
    get_opencode_config_dir_path,
)

INSTALLED_MANIFEST: list[tuple[str, str]] = [
    ("agents/*.md", "agents"),
    ("tools/*.ts", "tools"),
    ("commands/*.md", "commands"),
    ("plugins/*.ts", "plugins"),
    ("plugins/lib/inspector_general.ts", "plugins/lib"),
]


def run_opencode_uninstall(globally: bool = False) -> bool:
    """Remove methodology agents and tools from Opencode config directory.

    Only deletes files that were placed by install. Leaves package.json,
    node_modules, bun.lock, opencode.json(c) and any user-owned files
    untouched.

    :param bool globally: If True uninstall from XDG_CONFIG_HOME/opencode,
        otherwise from local .opencode in current directory
    :return: True if command completed, False otherwise
    :rtype: bool
    """
    src_root = _get_source_root()
    config_dir = get_opencode_config_dir_path(is_global=globally)

    print(f"Uninstalling from {config_dir}")

    removed = 0
    skipped = 0

    for src_pattern, dst_rel in INSTALLED_MANIFEST:
        if not src_pattern.endswith("*"):
            dst = config_dir / dst_rel
            if dst.exists():
                dst.unlink()
                removed += 1
                print(f"  Removed {dst_rel}")
            else:
                skipped += 1
        else:
            src_dir = src_root / Path(src_pattern).parent
            pattern = Path(src_pattern).name
            if not src_dir.exists():
                continue
            for src_file in src_dir.glob(pattern):
                dst = config_dir / dst_rel / src_file.name
                if dst.exists():
                    dst.unlink()
                    removed += 1
                    print(f"  Removed {dst_rel}/{src_file.name}")
                else:
                    skipped += 1

    print()
    print("Uninstall complete!")
    print(f"  Removed: {removed}")
    if skipped:
        print(f"  Not installed (skipped): {skipped}")

    return True


def _get_source_root() -> Path:
    """Return the root of the opencode source tree.

    Uses __file__ to locate the amphimixis-integrations/opencode directory.
    """
    self_path = Path(__file__).parent.resolve()
    project_root = self_path.parent.parent.parent.parent.resolve()
    return project_root / "amphimixis-integrations" / "opencode"
