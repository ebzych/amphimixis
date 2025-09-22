import pytest
from general import Build
from builder import run_command
import os

path = "/home/maria/Documents/proj/yaml-cpp/build"


def test_run_command_cmake():
    os.makedirs(path, exist_ok=True)
    command = "cmake .. -DYAML_CPP_BUILD_TESTS=ON"
    assert run_command(command, path) == True


def test_run_command_make():
    command = "make"
    assert run_command(command, path) == True
