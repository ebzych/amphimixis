"""Tests for the full launch of the application on a specific project"""

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_e2e_local_machine(clone_repo, create_working_space):
    """This end-to-end test validates that the pipeline can successfully process
    the yaml-cpp repository using the configuration file input_local.yaml.
    """
    repo_path = clone_repo("https://github.com/leethomason/tinyxml2")
    working_dir = create_working_space()
    orig_dir = Path.cwd()
    try:
        orig_file = Path(f"{orig_dir}/tests/integration/input_local.yaml")
        config_file = Path(f"{working_dir}/input.yml")
        add_jobs_cmd = [
            "bash",
            "-c",
            f"sed 's/jobs:/jobs: {os.cpu_count() or 8}/' {orig_file} > {config_file}",
        ]
        subprocess.check_call(
            add_jobs_cmd,
        )

        os.chdir(working_dir)
        command = [
            "python3",
            orig_dir / "amphimixis/amixis/__main__.py",
            "run",
            str(repo_path),
            "--events",
            "cycles",
        ]

        result = subprocess.run(command, check=False)

        assert result.returncode == 0

    finally:
        os.chdir(orig_dir)
