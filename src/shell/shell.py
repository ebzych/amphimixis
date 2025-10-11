"""Module for shell operations."""

import ipaddress
from ctypes import ArgumentError
from typing import Self

from general import MachineInfo

from .local_shell_handler import _LocalShellHandler
from .shell_interface import IShellHandler
from .ssh_shell_handler import _SSHHandler


class Shell:
    """Shell class to manage shell operations."""

    def __init__(self, machine: MachineInfo):
        self._shell: IShellHandler
        self.machine = machine

    def connect(self) -> Self:
        """Connect to the shell based on the IP address."""

        if self.machine.ip is None:
            self._shell = _LocalShellHandler()
            return self

        ip = ipaddress.ip_address(self.machine.ip)
        if ip.is_loopback:
            self._shell = _SSHHandler(
                str(ip),
                int(self.machine.auth.port),
                self.machine.auth.username,
                self.machine.auth.password,
            )
        else:
            raise ArgumentError(f"{self.machine.ip} is loopback address.")

        return self

    def run(self, command: str) -> None:
        """Run the command through the shell."""
        self._shell.run(command)

    def readline(self) -> str:
        """Read a line from the shell output."""
        return self._shell.readline()
