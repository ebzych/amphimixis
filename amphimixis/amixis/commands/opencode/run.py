"""Opencode run subcommand."""

from pathlib import Path
import subprocess


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
                "methodology-orchestrator",
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
