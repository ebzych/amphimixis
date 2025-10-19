"""Contain classes which represent machine"""

from dataclasses import dataclass
from .architecture import Arch


@dataclass
class MachineAuthenticationInfo:
    """Information about authentication on a remote machine

    :var str username: Username for authentication.
    :var str | None password: Password for authentication.
    Password can be set to None if an SSH agent is used.

    :var int port: Port number for the SSH connection.
    """

    username: str
    password: str | None
    port: int


@dataclass
class MachineInfo:
    """Information about the machine

    :var Arch arch: Architecture of the machine.
    :var str | None address: IP address or hostname of the remote machine.
    If address is None, the machine is considered to be local.

    :var MachineAuthenticationInfo auth: Authentication info for the machine.
    """

    arch: Arch
    address: str | None
    auth: MachineAuthenticationInfo | None
