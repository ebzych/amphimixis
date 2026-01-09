"""Module for configuring a new build"""

import pickle
from os import getcwd, path
from platform import machine as local_arch
from typing import Any

import yaml

from amphimixis.build_systems import build_systems_dict
from amphimixis.general import general
from amphimixis.general.constants import ANALYZED_FILE_NAME
from amphimixis.laboratory_assistant import LaboratoryAssistant
from amphimixis.logger import setup_logger
from amphimixis.shell import Shell
from amphimixis.validator import validate

DEFAULT_PORT = 22

_logger = setup_logger("configurator")


# pylint: disable=too-many-return-statements
def parse_config(project: general.Project, config_file_path: str) -> bool:
    """Main function to configure builds

    :rtype: bool
    :return: Outcome value :\n
         True if configuration succeeded
         False if configuration failed
    """

    if not path.exists(project.path):
        _logger.error("Incorrect project path @_@, check input arguments")
        return False

    project.builds = []

    if not validate(config_file_path):
        _logger.error("Incorrect input file")
        return False

    try:
        with open(config_file_path, "r", encoding="UTF-8") as file:
            input_config = yaml.safe_load(file)

            build_system = input_config.get("build_system")
            if build_system is None:
                if not (build_system := _get_analyzed_build_system()):
                    _logger.error("Did not find any proper build_system")
                    return False

            runner = input_config.get("runner")

            project.build_system = build_systems_dict[build_system.lower()]
            project.runner = build_systems_dict[runner.lower()]

            for build in input_config["builds"]:

                (
                    toolchain,
                    sysroot,
                    executables,
                    build_machine_info,
                    run_machine_info,
                    recipe_info,
                ) = _configure_build(input_config, build)

                if (
                    build_machine_info == {}
                    or run_machine_info == {}
                    or recipe_info == {}
                ):
                    return False

                if not _create_build(
                    project,
                    build_machine_info,
                    run_machine_info,
                    recipe_info,
                    executables,
                    toolchain,
                    sysroot,
                ):
                    return False

    except FileNotFoundError:
        _logger.error("Error opening file, check input data")
        return False

    _logger.info("Configuration completed successfully!")
    return True


def _configure_build(input_config: dict[str, Any], build: dict[str, Any]) -> tuple[
    general.Toolchain | None,
    str | None,
    list[str],
    str | dict[str, int | str],
    str | dict[str, int | str],
    dict[str, Any],
]:
    """Function to configure fields of a single build"""

    toolchain = None
    if toolchain_info := build.get("toolchain"):
        toolchain = create_toolchain(toolchain_info)

    sysroot = build.get("sysroot")
    if sysroot is None and toolchain is not None:
        sysroot = toolchain.sysroot

    executables = build.get("executables", [])

    build_machine_info = build["build_machine"]
    if str(build_machine_info).isdecimal():
        build_machine_info = _get_by_id(
            input_config["platforms"], build["build_machine"]
        )

    run_machine_info = build["run_machine"]
    if str(run_machine_info).isdecimal():
        run_machine_info = _get_by_id(input_config["platforms"], build["run_machine"])

    recipe_info = _get_by_id(input_config["recipes"], build["recipe_id"])

    return (
        toolchain,
        sysroot,
        executables,
        build_machine_info,
        run_machine_info,
        recipe_info,
    )


def _create_build(  # pylint: disable=R0913,R0914,R0917
    project: general.Project,
    build_machine_info: str | dict[str, int | str],
    run_machine_info: str | dict[str, int | str],
    recipe_info: dict[str, Any],
    executables: list[str],
    toolchain: general.Toolchain | None,
    sysroot: str | None,
) -> bool:
    """Function to create a new build and save its configuration to a Pickle file"""

    id_name_build_machine = (
        build_machine_info
        if isinstance(build_machine_info, str)
        else build_machine_info["id"]
    )
    id_name_run_machine = (
        run_machine_info
        if isinstance(run_machine_info, str)
        else run_machine_info["id"]
    )
    build_name = _generate_build_name(
        str(id_name_build_machine), str(id_name_run_machine), recipe_info["id"]
    )

    if isinstance(build_machine_info, str):
        if (
            build_machine := LaboratoryAssistant.find_platform(build_machine_info)
        ) is None:
            msg = f"Build '{build_name}': unknown build machine: '{build_machine_info}'"
            _logger.fatal(msg)
            raise ValueError(msg)
    else:
        build_machine = create_machine(build_machine_info)

    if isinstance(run_machine_info, str):
        if (run_machine := LaboratoryAssistant.find_platform(run_machine_info)) is None:
            msg = f"Build '{build_name}': unknown run machine: '{run_machine_info}'"
            _logger.fatal(msg)
            raise ValueError(msg)
    else:
        run_machine = create_machine(run_machine_info)

    if not _has_valid_arch(run_machine):
        return False

    config_flags = recipe_info.get("config_flags", "")
    compiler_flags = create_flags(recipe_info.get("compiler_flags"))

    build = general.Build(
        build_machine,
        run_machine,
        build_name,
        executables,
        toolchain,
        sysroot,
        compiler_flags,
        config_flags,
    )

    project.builds.append(build)

    config_path = path.join(getcwd(), f"{build_name}_config")
    with open(config_path, "wb") as file:
        pickle.dump(build, file)

    return True


def _generate_build_name(build_id: str, run_id: str, recipe_id: str) -> str:
    """Function to create path to build, depending on build, run and recipes ids"""

    return f"{build_id}_{run_id}_{recipe_id}"


def _get_by_id(items: list[dict[str, str]], target_id: int) -> dict[str, str]:
    """Function to find item in dict by id"""

    for item in items:
        id_ = item["id"]
        if not isinstance(id_, int):
            msg = f"Error: not integer id '{id_}' of item: {item}"
            _logger.fatal(msg)
            raise ValueError(msg)
        if id_ == target_id:
            return item

    _logger.error("Item id didn't match any existed id, check input file")
    return {}


def _has_valid_arch(machine: general.MachineInfo) -> bool:
    """Function to check whether run machine arch is valid"""

    if machine.address is None:
        if machine.arch.lower() not in local_arch().lower():
            _logger.error(
                "Invalid local machine arch: %s, your machine is %s",
                machine.arch.name.lower(),
                local_arch().lower(),
            )
            return False

    else:
        shell = Shell(machine).connect()
        error_code, stdout, _ = shell.run("uname -m")
        if error_code != 0:
            _logger.error(
                "An error occured during reading remote machine arch, check remote machine"
            )
            return False

        remote_arch = stdout[0][0]
        if machine.arch.lower() not in remote_arch.lower():
            _logger.error(
                "Invalid remote machine arch: %s, remote machine is %s",
                machine.arch.name.lower(),
                remote_arch.lower(),
            )
            return False

    return True


def _get_analyzed_build_system() -> str | None:
    """Function to get build system from analyzed project

    :rtype: str | None
    :return: Outcome value :\n
         Build system name if it was found
         None if build system was not found or
         analysis was not completed
    """

    try:
        with open(ANALYZED_FILE_NAME, "r", encoding="UTF-8") as file:
            analyzed = yaml.safe_load(file)
            if analyzed:
                build_system = analyzed[0].lower()
                if (
                    build_system in build_systems_dict
                ):  # take first (in priority) found build system
                    return build_system
            return None

    except FileNotFoundError:
        return None


def create_machine(machine_info: dict[str, int | str]) -> general.MachineInfo:
    """Function to create a new machine"""

    arch = str(machine_info.get("arch"))
    address = machine_info.get("address")
    address = str(address) if address is not None else None
    auth = None

    if address is not None:
        username = str(machine_info.get("username"))
        password = machine_info.get("password")
        password = str(password) if password is not None else None
        port = int(machine_info.get("port", DEFAULT_PORT))

        auth = general.MachineAuthenticationInfo(username, password, port)

    machine = general.MachineInfo(general.Arch(arch.lower()), address, auth)

    return machine


def create_toolchain(
    toolchain_dict: dict[str, str] | str,
) -> general.Toolchain | None:
    """Function to create a new toolchain"""

    if isinstance(toolchain_dict, str):
        return LaboratoryAssistant.find_toolchain_by_name(toolchain_dict)

    toolchain = general.Toolchain()
    for attr in toolchain_dict:
        if attr.lower() in general.ToolchainAttrs:
            toolchain.set(general.ToolchainAttrs(attr.lower()), toolchain_dict[attr])

        elif attr.lower() in general.CompilerFlagsAttrs:
            toolchain.set(
                general.CompilerFlagsAttrs(attr.lower()), toolchain_dict[attr]
            )

        elif attr.lower() == "sysroot":
            toolchain.sysroot = toolchain_dict[attr]

        else:
            _logger.info("Unknown toolchain attribute: %s, skipping...", attr.lower())

    return toolchain


def create_flags(
    compiler_flags_dict: dict[str, str] | None,
) -> general.CompilerFlags | None:
    """Function to create new flags"""

    if compiler_flags_dict is None:
        return compiler_flags_dict

    compiler_flags = general.CompilerFlags()
    for flag in compiler_flags_dict:
        if flag.lower() in general.CompilerFlagsAttrs:
            compiler_flags.set(
                general.CompilerFlagsAttrs(flag.lower()), compiler_flags_dict[flag]
            )
        else:
            _logger.info(
                "Unknown compiler flag attribute: %s, skipping...", flag.lower()
            )

    return compiler_flags
