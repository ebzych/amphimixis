"""Module for shell operations."""

import os
import socket
import subprocess
from ctypes import ArgumentError
from typing import List, Self, Tuple

from amphimixis import logger
from amphimixis.general import MachineInfo, Project, constants
from amphimixis.shell.local_shell_handler import _LocalShellHandler
from amphimixis.shell.shell_interface import IShellHandler
from amphimixis.shell.ssh_shell_handler import _SSHHandler

_READING_BARRIER_FLAG = "READING_BARRIER_FLAG"


# pylint: disable=too-many-instance-attributes
class Shell:
    """Shell class to manage shell operations.

    In case of local machine `bash` is used as shell.
    """

    def __init__(self, machine: MachineInfo, connect_timeout=5):
        self.logger = logger.setup_logger("SHELL")
        self._shell: IShellHandler
        self.machine = machine
        self.connect_timeout = connect_timeout
        self._project_workdir: str = ""
        self._homedir: str = ""
        self._is_connected: bool = False
        self._is_local: bool = False

    def connect(self) -> Self:
        """Connect to the shell of the machine."""

        if self.machine.address is None:
            self._shell = _LocalShellHandler()
            self._is_connected = True
            self._is_local = True
            return self

        if self.machine.auth is None:
            self.logger.error(
                "Remote machine [%s] has no authentication info", self.machine.address
            )

            raise ArgumentError(
                f"Remote machine [{self.machine.address}] has no authentication info"
            )

        try:
            socket.getaddrinfo(self.machine.address, None)
        except socket.gaierror as exception:
            self.logger.error("%s is unknown address", self.machine.address)
            raise ArgumentError(
                f"{self.machine.address} is unknown address"
            ) from exception

        self._shell = _SSHHandler(self.machine, self.connect_timeout)
        self._is_connected = True
        self._is_local = False

        return self

    def run(self, *commands: str) -> Tuple[int, List[List[str]], List[List[str]]]:
        """Run the commands through the shell.

        - Execute commands one by one until:
            non-zero return code occurs or
            OR
            all commands have been executed.


        :param str *commands: commands to be executed

        :rtype: Tuple[int, List[List[str]], List[List[str]]]
        :return: A tuple of three :\n
            - :int: error code of the last executed command
            - :List[List[str]]: List[str] is lines of the stdout of an executed command.
            - :List[List[str]]: List[str] is lines of the stderr of an executed command.
        """

        stdout: List[List[str]] = []
        stderr: List[List[str]] = []
        error_code = 0
        for cmd in commands:
            if error_code:
                break
            self._shell.run(cmd)

            # newline added in case of it is missing in the previous output line
            self._shell.run(f'echo "\n{_READING_BARRIER_FLAG}:$?"')
            self._shell.run(f'echo "\n{_READING_BARRIER_FLAG}">&2')
            cmd_stdout: List[str] = []
            cmd_stderr: List[str] = []
            while line := self._shell.stdout_readline():
                if line[: len(_READING_BARRIER_FLAG)] == _READING_BARRIER_FLAG:
                    error_code = int(line[len(_READING_BARRIER_FLAG) + 1 :])
                    del cmd_stdout[-1]
                    break
                cmd_stdout.append(line)
            stdout.append(cmd_stdout)

            while line := self._shell.stderr_readline():
                if line[:-1] == _READING_BARRIER_FLAG:
                    del cmd_stderr[-1]
                    break
                cmd_stderr.append(line)
            stderr.append(cmd_stderr)

        return (error_code, stdout, stderr)

    def copy_to_remote(self, source: str, destination: str) -> bool:
        """Send a file or folder to the target machine
        Absolute paths are needed

        :var str source: absolute path to a file or folder on the host machine
        :var str destination: absolute path to copy a file or folder to on the controlled machine

        :return: True if successfully copied else False
        """
        if self.machine.auth is None:
            _destination = destination
        else:
            _destination = (
                f"{self.machine.auth.username}@{self.machine.address}:{destination}"
            )

        return self._copy(source, _destination)

    def copy_to_host(self, source: str, destination: str) -> bool:
        """Gets a file or folder from the target machine
        Absolute paths are needed

        :var str source: absolute path to a file or folder on the controlled machine
        :var str destination: absolute path to copy a file or folder to on the host machine

        :return: True if successfully copied else False
        """

        if self.machine.auth is None:
            _source = source
        else:
            _source = f"{self.machine.auth.username}@{self.machine.address}:{source}"

        return self._copy(_source, destination)

    def get_project_workdir(self, project: Project) -> str:
        """Gets a working directory for amphimixis

        :var Project project: Project object to determine the project name

        :rtype: str
        :return: In case of remote machine: `~/${AMPHIMIXIS_DIRECTORY_NAME}/`.
                 In case of local machine: current working directory.
        """

        if self._project_workdir != "":
            return self._project_workdir

        if not self._is_connected:
            self.connect()

        if self._is_local:
            self._project_workdir = os.getcwd()
            return self._project_workdir

        self._project_workdir = os.path.join(
            self.get_home(),
            constants.AMPHIMIXIS_DIRECTORY_NAME,
            os.path.basename(os.path.normpath(project.path)) + "_builds",
        )

        return self._project_workdir

    def get_home(self) -> str:
        """Gets a home directory for current connection (user@machine)"""

        if self._homedir != "":
            return self._homedir

        if not self._is_connected:
            self.connect()

        error, stdout, _ = self.run("echo ~")

        if error != 0:
            self.logger.error("Can't get workdir for %s", self.machine.address)
            return ""

        self._homedir = stdout[0][0].strip()
        return self._homedir

    def _copy(self, source: str, destination: str) -> bool:
        if self.machine.auth is None:
            port = -1  # should be OK with local copying
            password = "nopasswd"
        else:
            port = self.machine.auth.port
            # if None or empty string, ssh-agent is supposed
            password = self.machine.auth.password or "nopasswd"

        self.logger.info("Copying %s -> %s", source, destination)
        error_code = subprocess.call(
            [
                "sshpass",
                "-p",
                password,
                "rsync",
                "--checksum",
                "--archive",
                "--recursive",
                "--mkpath",
                "--copy-links",
                "--hard-links",
                "--compress",
                "--log-file=./amphimixis.log",
                "--port",
                str(port),
                source,
                destination,
            ]
        )

        if error_code != 0:
            self.logger.error("Error %s -> %s", source, destination)
            return False

        self.logger.info("Success %s -> %s", source, destination)
        return True
