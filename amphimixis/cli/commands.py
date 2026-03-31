"""CLI command implementations for Amphimixis."""

import shutil
import tempfile
from os import path

from amphimixis import Builder, Profiler, Shell, analyze, general, parse_config
from amphimixis.general import IUI, NullUI, constants, tools
from amphimixis.general.general import ProjectStats
from amphimixis.perf_analyzer import main as compare_perf


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

    for build in project.builds:
        if not Builder.build_for_linux(project, build, ui):
            ui.mark_failed()
            return False
        ui.mark_success("Build passed!")
    return True


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

    if not obj:
        print("\n[!] No profiling data (.scriptout files) were generated.")
        print("\tPlease check amphimixis.log for details.")
    elif len(obj.keys()) == 1:
        print("\n[i] Only one profiling result was generated.")
        print("\tTo compare two results, run profiling again with a different build.")
        print("\tOnce you have two .scriptout files, compare them with:")
        print("\tamixis --compare <file1.scriptout> <file2.scriptout>")
    else:
        key1, key2 = list(obj.keys())[:2]
        executable = None
        for exe in obj[key1]:
            if exe in obj[key2]:
                executable = exe
                break

        if executable is None:
            print(
                "\tThere is no profiling results for the same executable in different build"
            )
            print("\b Maybe you should check profiling errors")
            return

        build1_name = obj[key1][executable].build_name
        build2_name = obj[key2][executable].build_name

        if build1_name is None or build2_name is None:
            print("Currupted project.stats file")
            return

        file1 = (
            tools.build_filename(build1_name, executable) + constants.PERF_SCRIPT_EXT
        )

        file2 = (
            tools.build_filename(build2_name, executable) + constants.PERF_SCRIPT_EXT
        )

        print("\n[>] To compare two profiling results, use:")
        print(f"\tamixis --compare {file1} {file2}")


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
