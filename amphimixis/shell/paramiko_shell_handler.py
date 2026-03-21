"""SSH shell handler implementation."""

import socket
from ctypes import ArgumentError

import paramiko

from amphimixis.general import MachineInfo
from amphimixis.shell.shell_interface import IShellHandler

_CLEAR_OUTPUT_FLAG = "CLEAR_OUTPUT_FLAG"


class _ParamikoHandler(IShellHandler):
    def __init__(self, machine: MachineInfo, connect_timeout: int = 10) -> None:
        if machine.auth is None or machine.address is None:
            raise ArgumentError("Authentication data is not provided")

        self.machine = machine
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(
                hostname=machine.address,
                port=machine.auth.port,
                username=machine.auth.username,
                password=machine.auth.password,
                timeout=connect_timeout,
                look_for_keys=True,
                allow_agent=True,
            )
        except (paramiko.SSHException, socket.error) as e:
            raise paramiko.SSHException(f"Can't connect to ssh {machine}: {e}")

        if (transport := self.client.get_transport()) is not None:
            transport.set_keepalive(60)
            self.chan = transport.open_session()
        else:
            raise ConnectionError("Can't get transport")

        self.chan.invoke_shell()
        self.chan.send("exec bash --norc --noprofile\n".encode("UTF-8"))

        self._send_marker()
        self._read_until_marker()

    def __del__(self) -> None:
        self.client.close()

    def run(self, command: str) -> None:
        try:
            self.chan.send((command.strip() + "\n").encode("UTF-8"))
        except socket.error as e:
            raise socket.error(f"Can't send command: {e}")

    def stdout_readline(self) -> str:
        line = ""
        while char := self.chan.recv(1).decode("UTF-8", "replace"):
            line += char
            if char == "\n":
                break

        return line

    def stderr_readline(self) -> str:
        line = ""
        while char := self.chan.recv_stderr(1).decode("UTF-8", "replace"):
            line += char
            if char == "\n":
                break

        return line

    def _send_marker(self):
        self.chan.send((f"echo {_CLEAR_OUTPUT_FLAG}\n").encode("UTF-8"))

    def _read_until_marker(self):
        while (line := self.stdout_readline()) != "" and _CLEAR_OUTPUT_FLAG not in line:
            pass
