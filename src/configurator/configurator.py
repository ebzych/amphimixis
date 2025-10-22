"""Module for configuring a new build"""

from os import path, getcwd
import pickle
import yaml
import general


def parse_config(project: general.Project) -> None:
    """Module enter function"""

    if not path.exists(project.path):
        raise FileNotFoundError("Incorrect project path @_@, check input arguments")

    project.builds = []
    try:
        with open("input.yml", "r", encoding="UTF-8") as f:
            input_config = yaml.safe_load(f)

            if not isinstance(input_config["build_system"], str):
                raise TypeError("Invalid build system type :(, check config file")
            project.build_system = general.build_systems_dict[
                input_config["build_system"].lower()
            ]

            if not isinstance(input_config["runner"], str):
                raise TypeError("Invalid runner type ^~^, check config file")
            project.runner = general.build_systems_dict[input_config["runner"].lower()]

            for build in input_config["builds"]:
                toolchain = None
                sysroot = None

                if "toolchain" in build:
                    if not isinstance(build["toolchain"], str):
                        raise TypeError("Invalid toolchain type, check config file")
                    toolchain = build["toolchain"]

                if "sysroot" in build:
                    if not isinstance(build["sysroot"], str):
                        raise TypeError("Invalid sysroot type, check config file")
                    sysroot = build["sysroot"]

                configure(
                    project,
                    get_by_id(input_config["platforms"], build["build_machine"]),
                    get_by_id(input_config["platforms"], build["run_machine"]),
                    get_by_id(input_config["recipes"], build["recipe_id"]),
                    toolchain,
                    sysroot,
                )

    except FileNotFoundError as e:
        print(f"Error opening file, check input data. {e}")

    print("Configuration completed successfully!")


def configure(
    project: general.Project,
    build_machine_info: dict[str, str],
    run_machine_info: dict[str, str],
    recipe_info: dict[str, str],
    toolchain: str | None,
    sysroot: str | None,
) -> None:
    """Function to configure a new build and save its configuration to a Pickle file"""

    build_path = generate_build_path(
        build_machine_info["id"], run_machine_info["id"], recipe_info["id"]
    )

    build_machine = create_machine(build_machine_info)
    run_machine = create_machine(run_machine_info)

    build = general.Build(build_machine, run_machine, build_path, toolchain, sysroot)

    build.config_flags = recipe_info["config_flags"]
    build.compiler_flags = recipe_info["compiler_flags"]

    project.builds.append(build)

    config = build.__dict__

    config_name = f"{build_path}_config"
    with open(config_name, "wb") as file:
        pickle.dump(config, file)


def create_machine(machine_info: dict[str, str]) -> general.MachineInfo:
    """Function to create a new machine"""

    if not isinstance(machine_info["arch"], str):
        raise TypeError("Invalid arch type, check config file")

    if "address" in machine_info:
        if not isinstance(machine_info["address"], str):
            raise TypeError("Invalid address type, check config file")

        if "username" not in machine_info or not isinstance(
            machine_info["username"], str
        ):
            raise TypeError(
                "Invalid username type or username does not exist, check config file"
            )

        address = machine_info["address"]
        username = machine_info["username"]
        password = None
        port = 22

        if "password" in machine_info:
            if not isinstance(machine_info["password"], str):
                raise TypeError("Invalid password type, check config file")
            password = machine_info["password"]

        if "port" in machine_info:
            if not isinstance(machine_info["port"], int):
                raise TypeError("Invalid port type, check config file")
            port = machine_info["port"]

        auth = general.MachineAuthenticationInfo(username, password, port)

        machine = general.MachineInfo(
            general.Arch(machine_info["arch"].lower()), address, auth
        )
    else:
        machine = general.MachineInfo(
            general.Arch(machine_info["arch"].lower()), None, None
        )

    return machine


def generate_build_path(build_id: str, run_id: str, recipe_id: str) -> str:
    """Function to create path to build, depending on build, run and recipes ids"""

    return path.join(getcwd(), f"{build_id}_{run_id}_{recipe_id}")


def get_by_id(items: list[dict[str, str]], target_id: str) -> dict[str, str]:
    """Finds platform or recipe by id"""

    for item in items:
        if item["id"] == target_id:
            return item

    raise LookupError("Item id didn't match any existed id, check input file")
