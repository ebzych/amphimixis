"""SSH shell handler implementation."""

import select
import subprocess
from ctypes import ArgumentError

from general import MachineInfo

from .shell_interface import IShellHandler

_CLEAR_OUTPUT_FLAG = b"CLEAR_OUTPUT_FLAG\n"


class _SSHHandler(IShellHandler):

    def __init__(self, machine: MachineInfo, connect_timeout: int = 5) -> None:
        if machine.auth is None:
            raise ArgumentError("Authentication data is not provided")

        self.connect_timeout = connect_timeout
        self.machine = machine
        # pylint: disable=consider-using-with
        self.ssh = subprocess.Popen(
            [
                "ssh",
                "-q",
                "-o",
                f"ConnectTimeout={connect_timeout}",
                "-p",
                str(machine.auth.port),
                f"{machine.auth.username}@{machine.address}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if self.ssh.stdin is None or self.ssh.stdout is None or self.ssh.stderr is None:
            raise BrokenPipeError()

        r, _, _ = select.select([self.ssh.stdout], [], [], connect_timeout)

        if not r or self.ssh.poll() is not None:
            raise ConnectionError("can't connect to ssh")

        self.ssh.stdin.write(b"echo ")
        self.ssh.stdin.write(_CLEAR_OUTPUT_FLAG)
        self.ssh.stdin.flush()
        for i in self.ssh.stdout:
            if i == _CLEAR_OUTPUT_FLAG:
                break

    def __del__(self) -> None:
        self.ssh.kill()
        self.ssh.wait()

    def run(self, command: str) -> None:
        if self.ssh.stdin is None:
            raise BrokenPipeError("Can't write to process' stdin")

        cmd_bytes = command.encode("UTF-8")

        self.ssh.stdin.write(cmd_bytes)
        self.ssh.stdin.write(b"\n")
        self.ssh.stdin.flush()

    def stdout_readline(self) -> str:
        if self.ssh.stdout is None:
            raise BrokenPipeError("Can't read from process' stdout")

        line_bytes = self.ssh.stdout.readline()
        line = line_bytes.decode("UTF-8")
        return line

    def stderr_readline(self) -> str:
        if self.ssh.stderr is None:
            raise BrokenPipeError("Can't read from process' stdout")

        line_bytes = self.ssh.stderr.readline()
        line = line_bytes.decode("UTF-8")
        return line

    def copy_to_remote(self, source: str, destination: str) -> None:
        if self.machine.auth is None:
            raise ArgumentError("Authentication data is not provided")

        subprocess.check_call(
            [
                "scp",
                "-o",
                f"ConnectTimeout={self.connect_timeout}",
                "-P",
                str(object=self.machine.auth.port),
                source,
                f"{self.machine.auth.username}@{self.machine.address}:{destination}",
            ]
        )
