"""Shell handler interface"""

from abc import ABC, abstractmethod


class IShellHandler(ABC):
    """Abstract base class for shell handlers."""

    @abstractmethod
    def run(self, command: str) -> None:
        """Run a command in the shell.

        :var str command: Command to be executed.
        """
        raise NotImplementedError

    @abstractmethod
    def stdout_readline(self) -> str:
        """Read a line from the shell stdout.

        :rtype: str
        :return: the next line from stdout
        """
        raise NotImplementedError

    @abstractmethod
    def stderr_readline(self) -> str:
        """Read a line from the shell stderr.

        :rtype: str
        :return: the next line from stderr
        """

    @abstractmethod
    def copy_to_remote(self, source: str, destination: str) -> bool:
        """Copy a file or folder from the host machine

        :var str source: absolute path to a file or folder on the host machine
        :var str destination: absolute path to copy a file or folder to on the target machine

        :return: True if successful copied else False
        """

    @abstractmethod
    def copy_to_host(self, source: str, destination: str) -> bool:
        """Copy a file or folder from the remote machine

        :var str source: absolute path to a file or folder on the host machine
        :var str destination: absolute path to copy a file or folder to on the target machine
        """
