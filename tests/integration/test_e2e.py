import subprocess
import os
from pathlib import Path
import yaml
import pytest


@pytest.mark.integration
def test_build_local_machine(clone_repo, create_working_space):
    repo_path = clone_repo("https://github.com/jbeder/yaml-cpp.git")
    working_dir = create_working_space()
    orig_dir = Path.cwd()
    try:
        os.chdir(working_dir)
        with open(
            orig_dir / "tests" / "integration" / "input_local.yaml",
            "r",
            encoding="utf-8",
        ) as file:
            config_content = yaml.safe_load(file)
        config_file = working_dir / "input.yml"
        with open(config_file, "w", encoding="utf-8") as file:
            yaml.dump(config_content, file)
        command = ["python3", orig_dir / "amixis.py", str(repo_path)]
        result = subprocess.run(command)

        assert result.returncode == 0

    finally:
        os.chdir(orig_dir)
