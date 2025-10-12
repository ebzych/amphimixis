"""Module for shell operations."""

import ipaddress
from typing import Self

from .shell_interface import IShellHandler
from .ssh_shell_handler import _SSHHandler
from .local_shell_handler import _LocalShellHandler


class Shell:
    """Shell class to manage shell operations."""

    def __init__(self, ip: str, port: str, username: str, password: str):
        self._shell: IShellHandler
        self.username = username
        self.password = password
        self.ip = ipaddress.ip_address(ip)
        self.port = port

    def connect(self) -> Self:
        """Connect to the shell based on the IP address."""
        if self.ip.is_loopback:
            self._shell = _LocalShellHandler()
        else:
            self._shell = _SSHHandler(
                str(self.ip), int(self.port), self.username, self.password
            )

        return self

    def run(self, command: str) -> None:
        """Run the command through the shell."""
        self._shell.run(command)

    def readline(self) -> str:
        """Read a line from the shell output."""
        return self._shell.readline()
