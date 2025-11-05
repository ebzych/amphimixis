"Make IBuildSystem implementation"

from amphimixis.general import Build, IBuildSystem, Project
from amphimixis.shell import Shell


class Make(IBuildSystem):
    """The Make implementation of IBuildSystem"""

    @staticmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        raise NotImplementedError

    @staticmethod
    # pylint: disable=unused-argument
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        if command != "":
            raise NotImplementedError

        shell = Shell(build.build_machine).connect()
        err, stdout, _ = shell.run("nproc")
        nproc = int(stdout[0][0])

        prompt = "make"
        if err == 0:
            if nproc > 1:
                nproc -= 1  # to prevent OM
            prompt += " -j" + str(nproc)

        return prompt
