"""OpenCode tool definitions for amphimixis."""

import json
import subprocess
from pathlib import Path


def status(project_path: str, config: str = None) -> dict:
    """Show status of all builds on different machines in JSON format.

    :param str project_path: Path to the project directory
    :param str config: Optional path to config file (default: input.yml)
    :return: Dictionary with build statuses
    :rtype: dict
    """
    cmd = ["python3", "-m", "amphimixis.amixis", "status", "--json", project_path]
    if config:
        cmd.extend(["--config", config])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_path)

    if result.returncode != 0:
        return {"error": result.stderr, "status": "failed"}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"output": result.stdout, "status": "raw"}
