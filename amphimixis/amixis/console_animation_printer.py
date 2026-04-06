"""Single-line spinner for build progress display"""

import sys

from amphimixis.core.general import IUI

INVITATION_TEMPLATE_LEN = 6  # template: "[][_] "
FG_YELLOW_COLOR = "\033[38;2;255;255;0m"
FG_RED_COLOR = "\033[38;2;255;0;0m"
FG_DEFAULT_COLOR = "\033[39m"


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

    def send_message(self, sender: str, message: str) -> None:
        """Print message to user with status mark 'I'

        :param str sender: Identifier name of sender module
        :param str message: Message to user"""
        word_len = len(sender) + INVITATION_TEMPLATE_LEN
        to_insert = f"\n{" " * word_len}"
        print(f"\r\033[K[{sender}][I] {message.replace("\n", to_insert)}")

    def send_warning(self, sender: str, warning: str) -> None:
        """Print warning to user with status mark 'W' and 'WARNING: ' in begin of message

        :param str sender: Identifier name of sender module
        :param str warning: Warning to user"""
        word_len = len(sender) + INVITATION_TEMPLATE_LEN
        to_insert = f"\n{" " * word_len}"
        print(
            f"\r\033[K{FG_YELLOW_COLOR}[{sender}][W] WARNING: {warning.replace("\n", to_insert)}{FG_DEFAULT_COLOR}"
        )

    def send_error(self, sender: str, err_msg: str) -> None:
        """Print error to user with status mark 'E' and 'ERROR: ' in begin of message

        :param str sender: Identifier name of sender module
        :param str error: Error message to user"""
        word_len = len(sender) + INVITATION_TEMPLATE_LEN
        to_insert = f"\n{" " * word_len}"
        print(
            f"\r\033[K{FG_RED_COLOR}[{sender}][E] ERROR: {err_msg.replace("\n", to_insert)}{FG_DEFAULT_COLOR}"
        )

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

        :param str message: message to display. If empty, leaves the previous message
        :param str build_id: Build identifier. If empty, leaves the previous identifier
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

        :param str error_message: Message for failed build (if empty, keep previous)
        :param str build_id: Build identifier. If empty, leaves the previous identifier
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
        else:
            symbol = self.braille[self.index]

        sys.stdout.write(f"\r\033[K[{self.build_id}][{symbol}] {self.message}")
        sys.stdout.flush()

    def finalize(self) -> None:
        """Move to next line."""

        sys.stdout.write("\n")
        sys.stdout.flush()
