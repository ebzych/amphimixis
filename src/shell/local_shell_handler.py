"""Local shell handler implementation."""

import os
import subprocess

from .shell_interface import IShellHandler


class _LocalShellHandler(IShellHandler):
    def __init__(self) -> None:
        default_shell = os.getenv("SHELL")
        if default_shell is None:
            raise TypeError("Can't get default shell path")

        # pylint: disable=consider-using-with
        self.shell = subprocess.Popen(
            [default_shell],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if (
            self.shell.stdin is None
            or self.shell.stdout is None
            or self.shell.stderr is None
        ):
            raise BrokenPipeError()

    def __del__(self) -> None:
        self.shell.kill()
        self.shell.wait()

    def run(self, command: str) -> None:
        if self.shell.stdin is None:
            raise BrokenPipeError("Can't write to process' stdin")

        cmd_bytes = command.encode("UTF-8")

        if self.shell.stdin.write(cmd_bytes) != len(cmd_bytes):
            raise IOError("Not all data has been written")

        if self.shell.stdin.write(b"\n") != 1:
            raise IOError("Not all data has been written")

        self.shell.stdin.flush()

    def stdout_readline(self) -> str:
        if self.shell.stdout is None:
            raise BrokenPipeError("Can't read from process' stdout")
        return self.shell.stdout.readline().decode()

    def stderr_readline(self) -> str:
        if self.shell.stderr is None:
            raise BrokenPipeError("Can't read from process' stderr")
        return self.shell.stderr.readline().decode()

    def copy_to_remote(self, source: str, destination: str) -> int:
        print("Copying files...")

        error_code = subprocess.call(
            [
                "rsync",
                "--checksum",
                "--archive",
                "--recursive",
                "--mkpath",
                "--copy-links",
                "--hard-links",
                "--compress",
                "--log-file=./amphimixis.log",
                source,
                destination,
            ]
        )

        if error_code != 0:
            print("Sources copying error.")
            return -1

        print("Successful copied.")
        return 0
