import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path


@pytest.fixture
def clone_repo():
    repo_paths = []

    def _clone_repo(repo_url):
        repo_path = tempfile.mkdtemp(prefix="temp_dir")
        command = ["git", "clone", repo_url, repo_path]
        subprocess.run(command)
        repo_paths.append(repo_path)
        return Path(repo_path)

    yield _clone_repo

    for path in repo_paths:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def create_working_space():
    working_dirs = []

    def _create_temp_file():
        working_dir = tempfile.mkdtemp(prefix="test_workspace_")
        working_dirs.append(working_dir)
        return Path(working_dir)

    yield _create_temp_file

    for dir in working_dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir, ignore_errors=True)
