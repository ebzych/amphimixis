"""CLI command implementations for Amphimixis."""

import os
import pickle
import shutil
import subprocess
import tempfile
from os import path
from pathlib import Path

import yaml

from amphimixis import (
    Builder,
    Profiler,
    Shell,
    analyze,
    general,
    laboratory_assistant,
    parse_config,
    validate,
)
from amphimixis.general import IUI, Build, NullUI, Project, constants, tools
from amphimixis.general.general import ProjectStats
from amphimixis.perf_analyzer import main as compare_perf

CONFIG_TEMPLATE = """# Amphimixis Configuration Template
# Uncomment and configure the fields below:

# Build system (optional, default: CMake)
# build_system: CMake

# Runner / low-level build system (optional, default: Make)
# runner: Make

platforms:
  # - id: 1                        # Unique platform id
  #   address:                     # IP/domain (omit for local machine)
  #   arch: x86                    # Architecture (e.g. x86, riscv64, aarch64)
  #   username: root               # SSH username (required for remote)
  #   password: secret             # SSH password (or use SSH keys)
  #   port: 22                     # SSH port (optional, default: 22)

recipes:
  # - id: 1                        # Unique recipe id
  #   config_flags: "-DCMAKE_BUILD_TYPE=RelWithDebInfo"  # Build configuration options
  #   compiler_flags:              # Compiler flags dictionary
  #     cxx_flags: "-O2"           # C++ compiler flags
  #   toolchain:                   # Toolchain configuration (dict or name)
  #     cxx_compiler: "/usr/bin/g++"
  #   sysroot: "/"                 # Path to system headers/libraries

builds:
  # - build_machine: 1             # platform_id to build on
  #   run_machine: 1                # platform_id to run on
  #   recipe_id: 1                  # recipe_id to use
  #   executables:                  # Executables to profile (relative to build dir)
  #     - test/run-tests
"""

TOOLCHAIN_TEMPLATE = """# Toolchain Configuration Template
# Uncomment and fill in the fields below:

# name: my_toolchain   # Required: unique toolchain name
# platform: riscv64   # Options: x86_64, riscv64, etc.

# Sysroot (optional)
# sysroot: /path/to/sysroot

# Toolchain attributes (uncomment and cpnfigure as needed)
# attributes:
#    # Compilers
#    # c_compiler: /usr/bin/riscv64-unknown-elf-gcc
#    # cxx_compiler: /usr/bin/riscv64-unknown-elf-g++

#    #Tools
#    # ar: /usr/bin/riscv64-unknown-elf-ar
#    # as: /usr/bin/riscv64-unknown-elf-as
#    # ld: /usr/bin/riscv64-unknown-elf-ld
#    # nm: /usr/bin/riscv64-unknown-elf-nm
#    # objcopy: /usr/bin/riscv64-unknown-elf-objcopy
#    # objdump: /usr/bin/riscv64-unknown-elf-objdump
#    # ranlib: /usr/bin/riscv64-unknown-elf-ranlib
#    # readelf: /usr/bin/riscv64-unknown-elf-readelf
#    # strip: /usr/bin/riscv64-unknown-elf-strip

#    # Compiler flags (optional)
#    # cflags: -O2 -march=rv64gc
#    # cxxflags: -O2 -march=rv64gc
"""

def run_analyze(project: general.Project, ui: IUI = NullUI()) -> bool:
    """Execute project analysis.

    :param Project project: Project instance to analyze
    :param IUI ui: User interface for progress display
    """
    project_name = path.basename(path.normpath(project.path))
    ui.update_message(project_name, "Analyzing project...")

    if not analyze(project):
        ui.mark_failed("Analysis failed. See amphimixis.log for details.")
        return False
    ui.mark_success("Analysis completed! See amphimixis.log for details.")
    return True


def run_build(
    project: general.Project, config_file_path: str, ui: IUI = NullUI()
) -> bool:
    """Execute project build.

    :param Project project: Project instance to build
    :param str config_file: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    if not project.builds and not parse_config(
        project, config_file_path=str(config_file_path), ui=ui
    ):
        return False

    there_are_built = False
    for build in project.builds:
        if Builder.build_for_linux(project, build, ui):
            there_are_built = True
            ui.mark_success("Build passed!")
        else:
            ui.mark_failed(build_id=build.build_name, error_message="Building failed")

    return there_are_built


def run_profile(
    project: general.Project,
    config_file_path: str,
    ui: IUI = NullUI(),
    events: list[str] | None = None,
) -> bool:
    """Execute project profiling.

    :param project: Project instance to profiler
    :param str config_file_path: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    if not project.builds and not parse_config(
        project, config_file_path=str(config_file_path), ui=ui
    ):
        return False

    setup_profiling_environment(project, ui)

    success = True

    for build in project.builds:
        if not build.successfully_built:
            continue
        profiler_ = Profiler(project, build, ui)
        successful_execs = profiler_.profile_all(events=events)
        profiler_.save_stats()
        profiler_.cleanup()
        # if empty return -> error
        # if build.executables is not empty, return not equal build.executables -> error
        # if build.executables is empty, return(found executables for profiling) not empty -> passed
        if not successful_execs or (
            build.executables and successful_execs != build.executables
        ):
            ui.mark_failed("Some executables failed to be profiled")
            success = False
        else:
            ui.mark_success("Profiling completed!")

    return success


def run_compare(
    filename1: str,
    filename2: str,
    target_events: None | list[str] = None,
    max_rows=20,
    ui: IUI = NullUI(),
) -> bool:
    """Compare two perf output files and print the top `max_rows`
    symbols with the most significant changes for specified events.

    :param str filename1: Path to first perf output file
    :param str filename2: Path to second perf output file
    :param list[str] target_events: List of event names to compare (or None for all)
    :param int max_rows: Maximum number of rows to display per event
    :param IUI ui: User interface for progress display
    """

    if not path.isfile(filename1):
        ui.mark_failed(f"File not found: {filename1}")
        return False
    if not path.isfile(filename2):
        ui.mark_failed(f"File not found: {filename2}")
        return False

    if (
        compare_perf(
            filename1, filename2, target_events=target_events, max_rows=max_rows
        )
        != 0
    ):
        ui.mark_failed("Comparison failed.")
        return False
    ui.mark_success("Comparison completed!")
    return True


def show_profiling_result(project: general.Project):
    """Show hint or warning after profiling, based on .scriptout files in current directory."""

    obj: ProjectStats = tools.load_project_stats(project)

    if not obj or not any(
        obj[build][exe].executable_run_success
        for build in obj.keys()
        for exe in obj[build]
    ):
        print("\n[!] No profiling data (.scriptout files) were generated.")
        print("\tPlease check amphimixis.log for details.")
        return

    if len(obj.keys()) == 1:
        print("\n[i] Only one profiling result was generated.")
        print("\tTo compare two results, run profiling again with a different build.")
        print("\tOnce you have two .scriptout files, compare them with:")
        print("\tamixis compare <file1.scriptout> <file2.scriptout>")
        return

    def _find_matching_exe() -> tuple[str, str, str]:
        found_build1 = None
        found_build2 = None
        found_executable = None
        build_keys = list(obj.keys())
        for build1_index in range(len(build_keys) - 1):
            for build2_key in build_keys[build1_index + 1 :]:
                build1 = obj[build_keys[build1_index]]
                build2 = obj[build2_key]

                exe_keys = set(obj[build_keys[build1_index]]) | set(obj[build2_key])

                for exe in exe_keys:
                    if (
                        build1[exe].executable_run_success
                        and build2[exe].executable_run_success
                    ):
                        found_build1 = build_keys[build1_index]
                        found_build2 = build2_key
                        found_executable = exe
                        return found_build1, found_build2, found_executable
        return "", "", ""

    build1, build2, exe = _find_matching_exe()
    if not all([build1, build2, exe]):
        print(
            "\tThere is no profiling results for the same executable in different build"
        )
        print("\b Maybe you should check profiling errors")
        return

    file1 = tools.build_filename(build1, exe) + constants.PERF_SCRIPT_EXT
    file2 = tools.build_filename(build2, exe) + constants.PERF_SCRIPT_EXT

    print("\n[>] To compare two profiling results, use:")
    print(f"\tamixis compare {file1} {file2}")


def setup_profiling_environment(project: general.Project, ui: general.IUI) -> bool:
    """
    Set up the profiling environment by copying the built binaries to the run machines.
    """
    success = True
    tmpdir = tempfile.mkdtemp("_amphimixis")
    for build in project.builds:
        if build.build_machine != build.run_machine:
            ui.update_message(build.build_name, "Copying built files to run machine")
            shell_build_machine = Shell(project, build.build_machine, ui=ui)
            shell_run_machine = Shell(project, build.run_machine, ui=ui)

            # copy builds
            build_path = path.join(
                shell_build_machine.get_project_workdir(), build.build_name
            )
            if not shell_build_machine.copy_to_host(build_path, tmpdir):
                ui.mark_failed("Can't download built files from build machine")
                success = False

            if not shell_run_machine.copy_to_remote(
                path.join(tmpdir, build.build_name),
                shell_run_machine.get_project_workdir(),
            ):
                ui.mark_failed("Can't transfer built files to run machine")
                success = False

            # copy source
            if not shell_run_machine.copy_to_remote(
                project.path, path.dirname(shell_run_machine.get_source_dir())
            ):
                ui.mark_failed("Can't transfer source code to run machine")
                success = False

    shutil.rmtree(tmpdir)
    return success


def open_alternate_term() -> None:
    """Uses Xterm control code to switch to an alternate terminal buffer"""
    print("\033[?1049h", end="")


def close_alternate_term() -> None:
    """Uses Xterm control code to return back to first terminal buffer"""
    print("\033[?1049l", end="")


def clean(*builds: Build) -> bool:
    """Clean builds directories"""
    project: Project
    try:
        project = tools.get_cache_project()
    except FileNotFoundError:
        print("Project file .project not found")
        return False
    success = True
    for b in builds:
        if not Builder.clean(project, b):
            success = False
    return success


def interactive_clean() -> bool:
    """Enumerate builds names and suggest choose which will be cleaned"""
    builds: dict[str, Build] = {}
    project: Project
    try:
        project = tools.get_cache_project()
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as file:
            builds = pickle.load(file)
    except FileNotFoundError:
        pass

    success = True
    try:
        for i, build_name in enumerate(builds.keys()):
            print(f"{i + 1}.\t{build_name}")
        nums = [
            int(n) - 1 for n in input("Enter the builds numbers to clean: ").split()
        ]

        for i, build in enumerate(builds.values()):
            if i in nums:
                if Builder.clean(project, build):
                    print(f"{build.build_name} was successfully cleaned")
                else:
                    success = False
                    print(f"{build.build_name} failed to clean")
    except ValueError:
        print("Not a number")
    except KeyboardInterrupt:
        print("Cancelled")
    return success


def run_add_input() -> bool:
    """Interactively create input.yml configuration file.

    Opens an editor with existing file if it exists, or with a template
    if not. Validates the result and saves to input.yml on success.
    """
    config_path = Path("input.yml")
    editor = os.environ.get("EDITOR", "nano")

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            current_content = f.read()
    else:
        current_content = CONFIG_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the configuration and save to validate.")
    print("The editor will reopen if validation fails.\n")

    while True:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write(current_content)
            temp_path = Path(f.name)

        try:
            subprocess.call([editor, str(temp_path)])
        except FileNotFoundError:
            print(f"Error: Editor '{editor}' not found.")
            print("Please set the EDITOR environment variable to a valid editor.")
            os.unlink(temp_path)
            return False
        except OSError as e:
            print(f"Error launching editor: {e}")
            os.unlink(temp_path)
            return False

        try:
            with open(temp_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except OSError as e:
            print(f"Error reading file: {e}")
            os.unlink(temp_path)
            return False

        if validate(str(temp_path)):
            try:
                shutil.move(str(temp_path), str(config_path))
            except OSError as e:
                print(f"Error saving file: {e}")
                return False
            print("Configuration file input.yml successfully created!")
            return True

        print("\nValidation failed. Please fix the errors above.")
        print("Editor will reopen for corrections...")
        try:
            input("Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            if temp_path.exists():
                os.unlink(temp_path)
            return False


# pylint: disable=too-many-branches,too-many-statements
def run_add_toolchain() -> bool:
    """Interactively add a toolchain to global config.

    Opens an editor with a toolchain template, validates the result,
    and adds the toolchain to global config (~/.config/amphimixis/toolbox.yml).
    """
    editor = os.environ.get("EDITOR", "nano")

    toolbox = laboratory_assistant.LaboratoryAssistant.parse_config_file()

    if "toolchains" not in toolbox:
        toolbox["toolchains"] = {}

    current_content = TOOLCHAIN_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the toolchain template and save to validate.")
    print("The editor will reopen if validation fails.\n")

    while True:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write(current_content)
            temp_path = Path(f.name)

        try:
            subprocess.call([editor, str(temp_path)])
        except FileNotFoundError:
            print(f"Error: Editor '{editor}' not found.")
            print("Please set the EDITOR environment variable to a valid editor.")
            os.unlink(temp_path)
            return False
        except OSError as e:
            print(f"Error launching editor: {e}")
            os.unlink(temp_path)
            return False

        try:
            with open(temp_path, "r", encoding="utf-8") as f:
                current_content = f.read()
        except OSError as e:
            print(f"Error reading file: {e}")
            os.unlink(temp_path)
            return False

        try:
            new_toolchain = yaml.safe_load(current_content)
        except yaml.YAMLError as e:
            print(f"\nYAML parse error: {e}")
            print("Editor will reopen for corrections...")
            try:
                input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        if not isinstance(new_toolchain, dict):
            print("\nError: Toolchain must be a dictionary.")
            print("Editor will reopen for corrections...")
            try:
                input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        if "name" not in new_toolchain or not new_toolchain["name"]:
            print("\nError: Toolchain must have a 'name' field.")
            print("Editor will reopen for corrections...")
            try:
                input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        toolchain_name = new_toolchain["name"]

        if toolchain_name in toolbox.get("toolchains", {}):
            print(f"\nWarning: Toolchain '{toolchain_name}' already exists.")
            print("Not overwriting. Please choose a different name.")
            print("Editor will reopen for corrections...")
            try:
                input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        target_arch = new_toolchain.get("target_arch")
        sysroot = new_toolchain.get("sysroot")
        platform = new_toolchain.get("platform")
        attributes = new_toolchain.get("attributes", {})

        if platform:
            platform_value = platform
        else:
            platform_value = "localhost"

        toolchain_data: dict = {"attributes": attributes}
        if target_arch:
            toolchain_data["target_arch"] = target_arch
        if sysroot:
            toolchain_data["sysroot"] = sysroot
        if platform:
            toolchain_data["platform"] = platform_value

        toolbox["toolchains"][toolchain_name] = toolchain_data

        try:
            laboratory_assistant.LaboratoryAssistant._dump_config(toolbox)
        except OSError as e:
            print(f"Error saving toolchain: {e}")
            if temp_path.exists():
                os.unlink(temp_path)
            return False

        if temp_path.exists():
            os.unlink(temp_path)
        print(f"Toolchain '{toolchain_name}' added successfully!")
        return True
