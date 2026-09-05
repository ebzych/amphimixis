"""Opencode install subcommand."""

import shutil
import string
import subprocess
from inspect import stack
from os import environ
from pathlib import Path


def run_opencode_install(is_global: bool = False) -> bool:
    """Install Amphimixis-AI agents and tools into Opencode config directory.

    :param bool is_global: If True install globally (XDG_CONFIG_HOME/opencode),
        otherwise locally (.opencode in current directory)
    :return: True if installation succeeded, False otherwise
    :rtype: bool
    """
    self_path = Path(__file__).parent.resolve()
    project_root = self_path.parent.parent.parent.parent.resolve()
    config_dir = get_opencode_config_dir_path(is_global=is_global)

    src_root = project_root / "amphimixis-integrations" / "opencode"
    src_general = project_root / "amphimixis-integrations" / "inspector_general.ts"

    print(f"Installing Amphimixis-AI agents and tools to {config_dir}")

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
        if label == "tools":
            _substitute_amixis_path(dst_dir)
        print(f"  Copied {count} {label}")

    if src_general.exists():
        dst_general = config_dir / "node_modules" / "inspector_general.ts"
        dst_general.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_general, dst_general)
        print("  Copied inspector_general to {Opencode config dir}/node_modules/")

    print("  Installing Bun dependencies (yaml, async-mutex, node-jq, ...)...")
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
                "node-jq",
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
    print("Amphimixis-AI agents and tools are now available in opencode.")

    return True


def _get_amixis_path() -> str:
    amixis_executable_path = [
        Path(el.filename)
        for el in stack()
        if "amixis" in el.filename or "__main__" in el.filename
    ][-1].resolve()

    if "__main__" in str(amixis_executable_path):
        src_dir = (
            amixis_executable_path.parent.parent.parent
        )  # {repo_path}/amphimixis/amixis/__main__.py
        return f"uv --project {src_dir} run python {str(amixis_executable_path)}"
    return str(amixis_executable_path)


def _substitute_amixis_path(tools_dir: Path) -> None:
    """Substitute the amixis executable path into copied tool files.

    Tools contain the `$AMIXIS_PATH` template placeholder in the `amixis`
    variable. At install time it is replaced with the resolved executable
    path so installed tools invoke the right binary.

    :param Path tools_dir: directory with freshly installed tool files
    """
    amixis_executable_path = _get_amixis_path()
    for tool_file in tools_dir.glob("*.ts"):
        content = tool_file.read_text(encoding="utf-8")
        if "$AMIXIS_PATH" not in content:
            continue
        content = string.Template(content).safe_substitute(
            AMIXIS_PATH=amixis_executable_path
        )
        tool_file.write_text(content, encoding="utf-8")


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
