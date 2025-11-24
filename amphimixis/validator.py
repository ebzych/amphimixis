"""Module for validating an existing input file"""

# pylint: disable=W0603, C0103

from ipaddress import ip_address
from re import compile as re_compile

import yaml

from amphimixis.build_systems import build_systems_dict
from amphimixis.general import general
from amphimixis.logger import setup_logger

DEFAULT_PORT = 22

_errors_count = 0

_logger = setup_logger("validator")


def validate(config_file_path: str) -> None:
    """Module enter funtcion"""

    try:
        with open(config_file_path, "r", encoding="UTF-8") as file:

            global _errors_count

            file_dict = yaml.safe_load(file)

            build_system = file_dict.get("build_system")
            if (
                not isinstance(build_system, str)
                or build_system.lower() not in build_systems_dict
            ):
                _logger.warning("Invalid build_system: %s", build_system)
                _errors_count += 1

            runner = file_dict.get("runner")
            if not isinstance(runner, str) or runner.lower() not in build_systems_dict:
                _logger.warning("Invalid runner: %s", runner)
                _errors_count += 1

            # validate platforms
            platforms = file_dict.get("platforms", {})
            if platforms is None:
                _logger.warning("Platforms not found")
                _errors_count += 1

            for platform in platforms:
                _is_valid_platform(platform)

            # validate recipes
            recipes = file_dict.get("recipes", {})
            if recipes is None:
                _logger.warning("Recipes not found")
                _errors_count += 1

            for recipe in recipes:
                _is_valid_recipe(recipe)

            # validate builds
            builds = file_dict.get("builds", {})
            if builds is None:
                _logger.warning("Builds not found")
                _errors_count += 1

            for build in builds:
                _is_valid_build(build)

        _logger.info("Validation completed, errors found: %s", _errors_count)

    except FileNotFoundError:
        _logger.error("File not found")


def _is_valid_platform(platform: dict[str, str]):
    """Function to check whether plafrom is valid"""

    global _errors_count

    pl_id = platform.get("id")
    if not isinstance(pl_id, int):
        _logger.warning("Invalid id in platform: %s", pl_id)
        _errors_count += 1

    arch = platform.get("arch")
    if not isinstance(arch, str) or arch.lower() not in general.Arch:
        _logger.warning("Invalid arch in platform %s: %s", pl_id, arch)
        _errors_count += 1

    address = platform.get("address")
    if address is not None and (
        not isinstance(address, str) or not _is_valid_address(address)
    ):
        _logger.warning("Invalid address in platform %s: %s", pl_id, address)
        _errors_count += 1

    username = platform.get("username")
    if (
        address is None and (username is not None and not isinstance(username, str))
    ) or (address is not None and not isinstance(username, str)):
        _logger.warning("Invalid username in platform %s: %s", pl_id, username)
        _errors_count += 1

    password = platform.get("password")
    if password is not None and not isinstance(password, str):
        _logger.warning("Invalid password in platform %s: %s", pl_id, password)
        _errors_count += 1

    port = platform.get("port", DEFAULT_PORT)
    if not isinstance(port, int) or not 1 <= port <= 65535:
        _logger.warning("Invalid port in platform %s: %s", pl_id, port)
        _errors_count += 1


def _is_valid_recipe(recipe: dict[str, str]):
    """Function to check whether recipe is valid"""

    global _errors_count

    re_id = recipe.get("id")
    if not isinstance(re_id, int):
        _logger.warning("Invalid id in recipe: %s", re_id)
        _errors_count += 1

    config_flags = recipe.get("config_flags")
    if not isinstance(config_flags, str):
        _logger.warning("Invalid config_flags in recipe %s: %s", re_id, config_flags)
        _errors_count += 1

    compiler_flags = recipe.get("compiler_flags")
    if not isinstance(compiler_flags, str):
        _logger.warning(
            "Invalid compiler_flags in recipe %s: %s", re_id, compiler_flags
        )
        _errors_count += 1


def _is_valid_build(build: dict[str, str]):
    """Function to check whether build is valid"""

    global _errors_count

    build_machine = build.get("build_machine")
    if not isinstance(build_machine, int):
        _logger.warning("Invalid build_machine in build: %s", build_machine)
        _errors_count += 1

    run_machine = build.get("run_machine")
    if not isinstance(run_machine, int):
        _logger.warning("Invalid run_machine in build: %s", run_machine)
        _errors_count += 1

    recipe_id = build.get("recipe_id")
    if not isinstance(recipe_id, int):
        _logger.warning("Invalid recipe_id in build: %s", recipe_id)
        _errors_count += 1

    toolchain = build.get("toolchain")
    if toolchain is not None and not isinstance(toolchain, str):
        _logger.warning("Invalid toolchain in build: %s", toolchain)
        _errors_count += 1

    sysroot = build.get("sysroot")
    if sysroot is not None and not isinstance(sysroot, str):
        _logger.warning("Invalid sysroot in build: %s", sysroot)
        _errors_count += 1


def _is_valid_address(address: str) -> bool:
    """Function to check whether address is valid"""

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
