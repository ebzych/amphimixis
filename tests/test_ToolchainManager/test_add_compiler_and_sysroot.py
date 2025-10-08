from src.general import ToolchainManager, MachineInfo, MachineAuthenticationInfo, Arch
from os import path, getlogin
import yaml


def test_adding_not_existing_toolchain_in_toolbox_file() -> None:
    """
    Test: Adding non-existing toolchain to the toolbox
    Expected: Toolchain appeared in the toolbox
    """
    path_to_toolchain: str = "/bin/g++-14"
    build_machine = MachineInfo(
        Arch["x86"], "333.666.069.404", MachineAuthenticationInfo("bzych", None, 8000)
    )
    toolchain = {"machine": build_machine.__dict__, "path": path_to_toolchain}
    yaml_toolchain_str: str
    yaml.safe_dump(toolchain, yaml_toolchain_str)
    with open(f"/home/{getlogin()}/.config/amphimixis/toolbox.yml", "+") as f_toolbox:
        for row in f_toolbox.read():
            if row == yaml_toolchain_str:
                pass
