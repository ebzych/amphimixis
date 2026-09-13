"""Opencode install subcommand."""

import json
import shutil
import string
import subprocess
from inspect import stack
from os import environ
from pathlib import Path

from amphimixis.amixis.commands.opencode._package_utils import (
    is_package_declared,
    load_package,
    save_package,
)

INSPECTOR_GENERAL_NAME = "inspector_general"
_INSPECTOR_GENERAL_PACKAGE_DIR = "inspector_general"
_BUN_DEPENDENCIES = [
    "yaml",
    "async-mutex",
    "unified",
    "remark-parse",
    "remark-gfm",
    "node-jq",
]


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

    package_json = config_dir / "package.json"
    _remove_legacy_inspector_general(config_dir)
    package_dir = _prepare_inspector_general_package(project_root)

    if package_dir is not None:
        if shutil.which("bun") is not None:
            print(f"  Installing {INSPECTOR_GENERAL_NAME} package...")
            if is_package_declared(package_json, INSPECTOR_GENERAL_NAME):
                _run_bun(("remove", INSPECTOR_GENERAL_NAME), config_dir)
            if not _run_bun(("add", f"file:{package_dir.resolve()}"), config_dir):
                return False
            print("  Installing Bun dependencies (yaml, async-mutex, node-jq, ...)...")
            if not _run_bun(("add", *_BUN_DEPENDENCIES), config_dir):
                return False
        else:
            print(
                "    bun not found — install it from https://bun.sh; "
                "inspector_general is declared in package.json, opencode "
                "will install it on its next dependency check"
            )
            _declare_inspector_general(package_json, package_dir)

    print()
    print("Installation complete!")
    print("  Agents:  ", len(list((config_dir / "agents").glob("*.md"))))
    print("  Tools:   ", len(list((config_dir / "tools").glob("*.ts"))))
    print("  Commands:", len(list((config_dir / "commands").glob("*.md"))))
    print("  Plugins: ", len(list((config_dir / "plugins").glob("*.ts"))))
    print()
    print("Amphimixis-AI agents and tools are now available in opencode.")

    return True


def _prepare_inspector_general_package(project_root: Path) -> Path | None:
    """Prepare the local inspector_general package mirroring the canonical file.

    ``bun add`` installs folder dependencies by mirroring the *real* files of
    the target directory into the config ``node_modules``, so the package
    directory must contain a ``package.json`` and a real ``inspector_general.ts``.
    The canonical file stays in place; the package directory is regenerated on
    every install and mirrors it.

    :param Path project_root: repository root
    :return: path to the prepared package directory, or None when the
        canonical source file is missing
    :rtype: Path | None
    """
    src_general = project_root / "amphimixis-integrations" / "inspector_general.ts"
    if not src_general.exists():
        return None

    package_dir = (
        project_root / "amphimixis-integrations" / _INSPECTOR_GENERAL_PACKAGE_DIR
    )
    package_dir.mkdir(parents=True, exist_ok=True)
    package = {
        "name": INSPECTOR_GENERAL_NAME,
        "version": "1.0.0",
        "type": "module",
        "main": "inspector_general.ts",
        "exports": {".": "./inspector_general.ts"},
    }
    (package_dir / "package.json").write_text(
        json.dumps(package, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(src_general, package_dir / "inspector_general.ts")
    return package_dir


def _declare_inspector_general(package_json: Path, package_dir: Path) -> None:
    """Declare the inspector_general dependency without bun.

    Fallback used when bun is unavailable: opencode's own dependency install
    resolves the ``file:`` folder dependency on its next run.
    """
    package = load_package(package_json)
    dependencies = package.setdefault("dependencies", {})
    dependencies[INSPECTOR_GENERAL_NAME] = f"file:{package_dir.resolve()}"
    save_package(package_json, package)


def _remove_legacy_inspector_general(config_dir: Path) -> None:
    """Remove the legacy node_modules/inspector_general.ts artifact.

    Older versions copied it undecelared, so opencode prunes it on its next
    reinstall; this cleanup only speeds that up.
    """
    legacy = config_dir / "node_modules" / "inspector_general.ts"
    if legacy.is_file():
        legacy.unlink()


def _run_bun(args: tuple[str, ...], cwd: Path) -> bool:
    """Run ``bun`` inside the config directory."""
    result = subprocess.run(["bun", *args], cwd=cwd, check=False)
    return result.returncode == 0


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
