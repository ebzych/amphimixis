"""Module for configuring a new build"""

from os import path, getcwd
from re import compile as re_compile
from ipaddress import ip_address
from platform import machine as pl_machine
import logging
import pickle
import yaml
from amphimixis.general import general
from amphimixis.shell import Shell

DEFAULT_PORT = 22

# fmt: off
def parse_config(project: general.Project) -> None:
    """Module enter function"""

    if not path.exists(project.path):
        raise FileNotFoundError("Incorrect project path @_@, check input arguments")

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    project.builds = []

    try:
        with open("input.yml", "r", encoding="UTF-8") as f:
            input_config = yaml.safe_load(f)

            build_system = input_config.get("build_system")
            if (
                not isinstance(build_system, str)
                or build_system.lower() not in general.build_systems_dict
            ):
                raise TypeError(f"Invalid build_system: {input_config["build_system"]}")

            runner = input_config.get("runner")
            if (
                not isinstance(runner, str)
                or runner.lower() not in general.build_systems_dict
            ):
                raise TypeError(f"Invalid runner: {input_config["runner"]}")

            project.build_system = general.build_systems_dict[build_system.lower()]
            project.runner = general.build_systems_dict[runner.lower()]

            for build in input_config["builds"]:

                toolchain = build.get("toolchain")
                if (toolchain is not None and
                    not isinstance(toolchain, str)):
                    raise TypeError(
                        f"Invalid toolchain: {build["toolchain"]}, check config file"
                    )

                sysroot = build.get("sysroot")
                if (sysroot is not None and
                    not isinstance(sysroot, str)):
                    raise TypeError(
                        f"Invalid sysroot: {build["sysroot"]}, check config file"
                    )

                create_build(
                    project,
                    get_by_id(input_config["platforms"], build["build_machine"]),
                    get_by_id(input_config["platforms"], build["run_machine"]),
                    get_by_id(input_config["recipes"], build["recipe_id"]),
                    toolchain,
                    sysroot,
                )

    except FileNotFoundError as e:
        logger.error("Error opening file, check input data %s", e)

    logger.info("Configuration completed successfully!")


def create_build(
    project: general.Project,
    build_machine_info: dict[str, str],
    run_machine_info: dict[str, str],
    recipe_info: dict[str, str],
    toolchain: str | None,
    sysroot: str | None,
) -> None:
    """Function to create a new build and save its configuration to a Pickle file"""

    build_path = generate_build_path(
        build_machine_info["id"], run_machine_info["id"], recipe_info["id"]
    )

    build_machine = create_machine(build_machine_info)
    run_machine = create_machine(run_machine_info)
    if (
        run_machine.address is not None
        and pl_machine().lower() != run_machine.arch.name.lower()
    ):
        raise TypeError(
            f"Invalid local machibe arch: {run_machine.arch.name.lower()}, your machine is {pl_machine().lower()}"
        )

    build = general.Build(build_machine, run_machine, build_path, toolchain, sysroot)

    build.config_flags = recipe_info["config_flags"]
    build.compiler_flags = recipe_info["compiler_flags"]

    project.builds.append(build)

    config_name = f"{build_path}_config"
    with open(config_name, "wb") as file:
        pickle.dump(build, file)


def create_machine(machine_info: dict[str, str]) -> general.MachineInfo:
    """Function to create a new machine"""

    arch = machine_info.get("arch")
    if (not isinstance(arch, str) or
        arch.lower() not in general.Arch):
        raise TypeError(
            f"Invalid arch in platform {machine_info["id"]}: {machine_info["arch"]}"
        )

    address = machine_info.get("address")
    if (address is not None and
        (not isinstance(address, str) or
        not is_valid_address(address))):
        raise TypeError(
            f"Invalid address in platform {machine_info["id"]}: {machine_info["address"]}"
        )
    
    auth = None

    if address is not None:
        username = machine_info.get("username")
        if not isinstance(username, str):
            raise TypeError(
                f"Invalid username in platform {machine_info["id"]}: {machine_info["username"]}"
            )

        password = machine_info.get("password")
        if (password is not None and
            not isinstance(password, str)):
            raise TypeError(
                f"Invalid password in platform {machine_info["id"]}: {machine_info["password"]}"
            )

        port = machine_info.get("port", DEFAULT_PORT)
        if (not isinstance(port, int) or
            not 1 <= port <= 65535):
            raise TypeError(
                f"Invalid port in platform {machine_info["id"]}: {machine_info["port"]}"
            )

        auth = general.MachineAuthenticationInfo(username, password, port)

    machine = general.MachineInfo(general.Arch(arch.lower()), address, auth)

    return machine


def generate_build_path(build_id: str, run_id: str, recipe_id: str) -> str:
    """Function to create path to build, depending on build, run and recipes ids"""

    return path.normpath(path.join(getcwd(), f"{build_id}_{run_id}_{recipe_id}"))


def get_by_id(items: list[dict[str, str]], target_id: str) -> dict[str, str]:
    """Function to find platform or recipe by id"""

    for item in items:
        if item["id"] == target_id:
            return item

    raise LookupError("Item id didn't match any existed id, check input file")


def _is_valid_address(address: str) -> bool:
    """Function to check whether addtess id valid"""

    try:
        ip_address(address)
        return True
    except ValueError:
        pass

    if all(part.isdigit() for part in address.rstrip(".").split(".")):
        return False

    hostname_pattern = re_compile(
        r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
        r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
    )
    return bool(hostname_pattern.match(address))
