"""Module for validating an existing input file"""

# pylint: disable=W0603, C0103

from ipaddress import ip_address
from os import path
from re import compile as re_compile
from types import NoneType
from typing import Any

import yaml

from amphimixis.build_systems import build_systems_dict, runners_dict
from amphimixis.general import general, NullUI, IUI
from amphimixis.laboratory_assistant import LaboratoryAssistant
from amphimixis.logger import setup_logger

DEFAULT_PORT = 22

_errors_count = 0

_logger = setup_logger("validator")
_ui: IUI = NullUI()


def validate(config_file_path: str, ui: IUI = NullUI()) -> bool:
    """Main function to validate config file

    :rtype: bool
    :return: Outcome value :\n
         True if config is valid
         False if config is invalid or file not exists
    """
    global _ui
    _ui = ui

    if not path.exists(config_file_path):
        _logger.error("Config file not found")
        return False

    with open(config_file_path, "r", encoding="UTF-8") as file:
        file_dict = yaml.safe_load(file)

        build_system = file_dict.get("build_system")
        if (
            isinstance(build_system, str)
            and str(build_system).lower() not in build_systems_dict
        ):
            _notify_about_error(f"Invalid build_system: {build_system}")

        runner = file_dict.get("runner")
        if isinstance(runner, str) and runner.lower() not in runners_dict:
            _notify_about_error(f"Invalid runner: {runner}")

        # validate platforms
        platforms = file_dict.get("platforms", {})
        if platforms == {}:
            _notify_about_error("Platforms not found")

        for platform in platforms:
            _is_valid_platform(platform)

        # validate recipes
        recipes = file_dict.get("recipes", {})
        if recipes == {}:
            _notify_about_error("Recipes not found")

        for recipe in recipes:
            _is_valid_recipe(recipe)

        # validate builds
        builds = file_dict.get("builds", {})
        if builds == {}:
            _notify_about_error("Builds not found")

        for build in builds:
            _is_valid_build(build)

    _logger.info("Validation completed, errors found: %s", _errors_count)

    return _errors_count == 0


def _is_valid_platform(platform: dict[str, int | str]):
    """Function to check whether plafrom is valid"""

    pl_id = platform.get("id")
    if not isinstance(pl_id, int):
        _notify_about_error(f"Invalid id in platform: {pl_id}")

    arch = platform.get("arch")
    if not isinstance(arch, str) or arch.lower() not in general.Arch:
        _notify_about_error(f"Invalid arch in platform {pl_id}: {arch}")

    address = platform.get("address")
    if address is not None and (
        not isinstance(address, str) or not _is_valid_address(address)
    ):
        _notify_about_error(f"Invalid address in platform {pl_id}: {address}")

    username = platform.get("username")
    if (
        address is None and (username is not None and not isinstance(username, str))
    ) or (address is not None and not isinstance(username, str)):
        _notify_about_error(f"Invalid username in platform {pl_id}: {username}")

    password = platform.get("password")
    if password is not None and not isinstance(password, int | str):
        _notify_about_error(f"Invalid password in platform {pl_id}: {password}")

    port = platform.get("port", DEFAULT_PORT)
    if not isinstance(port, int) or not 1 <= port <= 65535:
        _notify_about_error(f"Invalid port in platform {pl_id}: {port}")


def _is_valid_recipe(recipe: dict[str, int | str]):
    """Function to check whether recipe is valid"""

    re_id = recipe.get("id")
    if not isinstance(re_id, int):
        _notify_about_error(f"Invalid id in recipe: {re_id}")

    config_flags = recipe.get("config_flags")
    if not isinstance(config_flags, str | NoneType):
        _notify_about_error(f"Invalid config_flags in recipe {re_id}: {config_flags}")

    compiler_flags = recipe.get("compiler_flags")
    if not isinstance(compiler_flags, dict | NoneType):
        _notify_about_error(
            f"Invalid compiler_flags in recipe {re_id}: {compiler_flags}"
        )

    if isinstance(compiler_flags, dict):
        for attr in compiler_flags:
            if not isinstance(attr, str):
                _notify_about_error(
                    f"Recipe {re_id}: invalid compiler_flags: invalid attribute '{attr}'"
                )
                continue
            if attr.lower() not in general.CompilerFlagsAttrs:
                _notify_about_error(
                    f"Recipe {re_id}: invalid compiler_flags: unknown attribute '{attr}'"
                )

    toolchain = recipe.get("toolchain")
    _is_valid_toolchain(toolchain)

    sysroot = recipe.get("sysroot")
    if sysroot is not None and not isinstance(sysroot, str):
        _notify_about_error(f"Invalid sysroot in build: {sysroot}")

    jobs = recipe.get("jobs")
    if jobs is not None and (not isinstance(jobs, int) or jobs <= 0):
        _notify_about_error(f"Invalid jobs number in recipe")


def _is_valid_build(build: dict[str, int | str]):
    """Function to check whether build is valid"""

    build_machine = build.get("build_machine")
    if not isinstance(build_machine, int | str):
        _notify_about_error(f"Invalid build_machine in build: {build_machine}")

    if isinstance(build_machine, str) and not LaboratoryAssistant.find_platform(
        build_machine
    ):
        _notify_about_error(f"Unknown build machine: {build_machine}")

    run_machine = build.get("run_machine")
    if not isinstance(run_machine, int | str):
        _notify_about_error(f"Invalid run_machine in build: {run_machine}")

    if isinstance(run_machine, str) and not LaboratoryAssistant.find_platform(
        run_machine
    ):
        _notify_about_error(f"Unknown run machine: {run_machine}")

    recipe_id = build.get("recipe_id")
    if not isinstance(recipe_id, int):
        _notify_about_error(f"Invalid recipe_id in build: {recipe_id}")

    executables = build.get("executables")
    if executables is not None and not isinstance(executables, list):
        _notify_about_error(f"Invalid executables in build: {executables}")


def _is_valid_toolchain(toolchain: Any) -> None:

    if not isinstance(toolchain, dict | str | NoneType):
        _notify_about_error(f"Invalid toolchain in build: '{toolchain}'")

    if isinstance(toolchain, str) and not LaboratoryAssistant.find_toolchain_by_name(
        toolchain
    ):
        _notify_about_error(f"Unknown toolchain '{toolchain}'")

    if isinstance(toolchain, dict):
        for attr, value in toolchain.items():
            if not isinstance(attr, str):
                _notify_about_error(f"Invalid toolchain: invalid attribute '{attr}'")
                continue
            if attr.lower() in general.ToolchainAttrs:
                if not path.isabs(value):
                    _notify_about_error(
                        f"Invalid toolchain: {attr}: path '{value}' is not absolute"
                    )
            elif attr.lower() not in general.CompilerFlagsAttrs and attr != "sysroot":
                _notify_about_error(f"Invalid toolchain: unknown attribute '{attr}'")


def _is_valid_address(address: str) -> bool:
    """Function to check whether address is valid

    :rtype: bool
    :return: Outcome value :\n
         True if address is valid
         False if address is invalid
    """

    try:
        ip_address(address)
        return True
    except ValueError:
        if all(part.isdigit() for part in address.rstrip(".").split(".")):
            return False

        # this string checks whether domain name is valid, here some rules:
        # 1. Length <= 253
        # 2. Separate part length <= 63
        # 3. Contains only letters, digits and dash
        # 4. Doesn't start or end with dash
        # 5. May have dot at the end
        hostname_pattern = re_compile(
            r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
            r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
        )
        return bool(hostname_pattern.match(address))


def _notify_about_error(msg: str) -> None:
    """Function that handles messages due to invalid fields in config"""

    global _errors_count
    global _ui
    _errors_count += 1
    _logger.error(msg)
    _ui.send_error("Config", msg)
