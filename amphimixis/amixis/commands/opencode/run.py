"""Opencode run subcommand."""

import subprocess
from pathlib import Path


def run_opencode_run(prompt: str) -> bool:
    """Run Opencode with the given prompt.

    :param str prompt: prompt to pass to Opencode
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """
    try:
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
