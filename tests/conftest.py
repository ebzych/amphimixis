"""Helper functions for tests"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def clone_repo():
    """The fixture for cloning a repository from GitHub to a temporary directory"""
    repo_paths = []

    def _clone_repo(repo_url):
        repo_path = tempfile.mkdtemp(prefix="temp_dir")
        command = ["git", "clone", repo_url, repo_path]
        subprocess.run(command, check=True)
        repo_paths.append(repo_path)
        return Path(repo_path)

    yield _clone_repo

    for path in repo_paths:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def create_working_space():
    """The ficture for creating a temporary working directory"""
    working_dirs = []

    def _create_temp_file():
        working_dir = tempfile.mkdtemp(prefix="test_workspace_")
        working_dirs.append(working_dir)
        return Path(working_dir)

    yield _create_temp_file

    for dir_ in working_dirs:
        if os.path.exists(dir_):
            shutil.rmtree(dir_, ignore_errors=True)
