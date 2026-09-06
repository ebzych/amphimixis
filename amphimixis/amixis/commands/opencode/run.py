"""Opencode run subcommand."""

import shlex
import shutil
import subprocess
from pathlib import Path

from amphimixis.amixis.commands.opencode.install import (
    get_opencode_config_dir_path,
)

JQ_FILTER = 'select(.type == "text") | .part.text'


def run_opencode_run(prompt: str, package_mode: bool = False) -> bool:
    """Run Opencode with the given prompt.

    :param str prompt: prompt to pass to Opencode
    :param bool package_mode: if True run non-interactively and print only
        text messages from the session filtered with jq
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """
    try:
        if package_mode:
            return _run_opencode_run_package_mode(prompt)

        subprocess.run(
            [
                "opencode",
                "--agent",
                "amphimixis",
                "--prompt",
                prompt,
                Path(".").resolve(),
            ],
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running opencode: {e}")
        return False


def _run_opencode_run_package_mode(prompt: str) -> bool:
    """Run Opencode non-interactively and print only its text messages.

    Uses `opencode run --format json` piped through `jq` to extract only
    messages of `text` type from the session output.

    :param str prompt: prompt to pass to Opencode
    :return: True if command succeeded, False otherwise
    """
    jq_path = _resolve_jq()
    if jq_path is None:
        print(
            "jq is required for --package-mode. "
            "Install it with `amixis opencode install` or from https://jqlang.org"
        )
        return False

    command = (
        "opencode run --format json --agent amphimixis "
        + shlex.quote(prompt)
        + " | "
        + jq_path
        + " -r "
        + shlex.quote(JQ_FILTER)
    )
    print(command)
    subprocess.run(command, shell=True, check=True)
    return True


def _resolve_jq() -> str | None:
    """Give path to a jq executable, if the one is available.

    Checks the system PATH first, then the jq binary installed into the
    Opencode config directory as part of the `node-jq` Bun package.
    """
    system_jq = shutil.which("jq")
    if system_jq is not None:
        return shlex.quote(system_jq)

    for global_path in (False, True):
        config_dir = get_opencode_config_dir_path(is_global=global_path)
        node_jq = config_dir / "node_modules" / "node-jq" / "node-jq"
        if node_jq.exists():
            return "bun run node-jq"

    return None
