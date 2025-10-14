"""Module for shell operations."""

import socket
from ctypes import ArgumentError
from typing import List, Self, Tuple

from general import MachineInfo

from .local_shell_handler import _LocalShellHandler
from .shell_interface import IShellHandler
from .ssh_shell_handler import _SSHHandler

_READING_BARRIER_FLAG = "READING_BARRIER_FLAG"


class Shell:
    """Shell class to manage shell operations.

    In case of local machine $SHELL is used as shell.
    """

    def __init__(self, machine: MachineInfo, connect_timeout=5):
        self._shell: IShellHandler
        self.machine = machine
        self.connect_timeout = connect_timeout

    def connect(self) -> Self:
        """Connect to the shell of the machine."""

        if self.machine.address is None:
            self._shell = _LocalShellHandler()
            return self

        if self.machine.auth is None:
            raise ArgumentError(
                f"Remote machine [{self.machine.address}] has no authentication info"
            )

        try:
            socket.getaddrinfo(self.machine.address, None)
        except socket.gaierror as exception:
            raise ArgumentError(
                f"{self.machine.address} is unknown address"
            ) from exception

        self._shell = _SSHHandler(self.machine, self.connect_timeout)

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
            - :List[List[str]]: lines from stdout of each command
            - :List[List[str]]: lines from stderr of each command
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
            self._shell.run(f'echo "\n{_READING_BARRIER_FLAG}:$?">&2')
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
                if line[: len(_READING_BARRIER_FLAG)] == _READING_BARRIER_FLAG:
                    error_code = int(line[len(_READING_BARRIER_FLAG) + 1 :])
                    del cmd_stderr[-1]
                    break
                cmd_stderr.append(line)
            stderr.append(cmd_stderr)

        return (error_code, stdout, stderr)
