"""Single-line spinner for build progress display"""

import sys

from amphimixis.general import IUI


class ConsoleAnimationPrinter(IUI):
    """Single-line console spinner implementation of IUI."""

    braille: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    build_id: str
    index: int
    message: str
    status: str

    def __init__(self):
        self.build_id = ""
        self.index = 0
        self.message = ""
        self.status = "running"

    def print_message(self, sender: str, message: str) -> None:
        """Print message to user with status mark 'I'

        :param str sender: Identifier name of sender module
        :param str message: Message to user"""
        self.status = "info"
        self.build_id = sender
        self.message = message
        self.draw()
        self.finalize()

    def print_warning(self, sender: str, warning: str) -> None:
        """Print warning to user with status mark 'W' and 'WARNING: ' in begin of message

        :param str sender: Identifier name of sender module
        :param str warning: Warning to user"""
        self.status = "warning"
        self.build_id = sender
        self.message = "WARNING: " + warning
        self.draw()
        self.finalize()

    def update_message(self, build_id: str, message: str) -> None:
        """Update build_id and message.

        :param str build_id: Build identifier
        :param str message: Message describing current build phase
        """

        if self.build_id != build_id:
            self.status = "running"
            self.index = 0

        self.build_id = build_id
        self.message = message
        self.draw()

    def step(self) -> None:
        """Move to next spinner."""

        self.index = (self.index + 1) % len(self.braille)
        self.draw()

    def mark_success(self, message: str = "", build_id: str = "") -> None:
        """Mark as successful.

        :param str message: message to display.
        If empty, leaves the previous message
        :param str build_id: Build identifier.
        If empty, leaves the previous identifier
        """

        self.status = "success"
        if build_id:
            self.build_id = build_id

        if message:
            self.message = message

        self.draw()
        self.finalize()

    def mark_failed(self, error_message: str = "", build_id: str = "") -> None:
        """Mark as failed and optionally update message.

        :param str error_message: Message to display for failed build.
        If empty, leaves the previous message
        :param str build_id: Build identifier.
        If empty, leaves the previous identifier
        """

        self.status = "failed"

        if build_id:
            self.build_id = build_id

        if error_message:
            self.message = error_message

        self.draw()
        self.finalize()

    def draw(self) -> None:
        """Draw current state to stdout."""

        if self.status == "success":
            symbol = "✓"
        elif self.status == "failed":
            symbol = "✗"
        elif self.status == "info":
            symbol = "I"
        elif self.status == "warning":
            symbol = "W"
        else:
            symbol = self.braille[self.index]

        sys.stdout.write(f"\r\033[K[{self.build_id}][{symbol}] {self.message}")
        sys.stdout.flush()

    def finalize(self) -> None:
        """Move to next line."""

        sys.stdout.write("\n")
        sys.stdout.flush()
