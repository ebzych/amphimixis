"""Single-line spinner for build progress display."""

from enum import Enum, StrEnum

from amphimixis.core.general import IUI

INVITATION_TEMPLATE_LEN = len("[][_] ")


class TermAttrs(StrEnum):
    """Attributes for printing in terminal.

    Represents Linux control characters.
    """

    ERASE_LINE = "\r\033[K"
    FG_GREEN_COLOR = "\033[38;2;120;255;0m"
    FG_YELLOW_COLOR = "\033[38;2;255;210;0m"
    FG_RED_COLOR = "\033[38;2;255;0;100m"
    FG_DEFAULT_COLOR = "\033[0m"
    BOLD_FONT = "\033[1m"


class BuildStatus(Enum):
    """Status values of build preparing."""

    FAILED = 0
    SUCCESS = 1
    RUNNING = 2


class ConsoleAnimationPrinter(IUI):
    """Single-line console spinner implementation of IUI."""

    braille: list[str] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    build_id: str
    index: int
    message: str
    status: BuildStatus

    def __init__(self):
        self.build_id = ""
        self.index = 0
        self.message = ""
        self.status = BuildStatus.RUNNING

    def send_message(self, sender: str, message: str) -> None:
        """Print message to user with status mark 'I'.

        :param str sender: Identifier name of sender module
        :param str message: Message to user
        """
        self._send_with_decorators(sender, "I", message, TermAttrs.FG_DEFAULT_COLOR)

    def send_warning(self, sender: str, warning: str) -> None:
        """Print warning to user with status mark 'W'.

        :param str sender: Identifier name of sender module
        :param str warning: Warning to user
        """
        self._send_with_decorators(sender, "W", warning, TermAttrs.FG_YELLOW_COLOR)

    def send_error(self, sender: str, error: str) -> None:
        """Print error to user with status mark 'E'.

        :param str sender: Identifier name of sender module
        :param str error: Error message to user
        """
        self._send_with_decorators(sender, "E", error, TermAttrs.FG_RED_COLOR)

    def update_message(self, build_id: str, message: str) -> None:
        """Update build_id and message.

        :param str build_id: Build identifier
        :param str message: Message describing current build phase
        """
        if self.build_id != build_id:
            self.status = BuildStatus.RUNNING
            self.index = 0

        self.build_id = build_id
        self.message = message
        self._draw()

    def step(self) -> None:
        """Move to next spinner."""
        self.index = (self.index + 1) % len(self.braille)
        self._draw()

    def mark_success(self, message: str = "", build_id: str = "") -> None:
        """Mark as successful.

        :param str message: message to display. If empty, leaves the previous message
        :param str build_id: Build identifier. If empty, leaves the previous identifier
        """
        self.status = BuildStatus.SUCCESS
        if build_id:
            self.build_id = build_id

        if message:
            self.message = message

        self._draw()
        print()

    def mark_failed(self, error_message: str = "", build_id: str = "") -> None:
        """Mark as failed and optionally update message.

        :param str error_message: Message for failed build (if empty, keep previous)
        :param str build_id: Build identifier. If empty, leaves the previous identifier
        """
        self.status = BuildStatus.FAILED

        if build_id:
            self.build_id = build_id

        if error_message:
            self.message = error_message

        self._draw()
        print()

    def _draw(self) -> None:
        """Draw current state to stdout."""
        if self.status == BuildStatus.SUCCESS:
            symbol = f"{TermAttrs.FG_GREEN_COLOR}✓{TermAttrs.FG_DEFAULT_COLOR}"
        elif self.status == BuildStatus.FAILED:
            symbol = f"{TermAttrs.FG_RED_COLOR}✗{TermAttrs.FG_DEFAULT_COLOR}"
        else:
            symbol = self.braille[self.index]

        symbol = f"{TermAttrs.BOLD_FONT}{symbol}{TermAttrs.FG_DEFAULT_COLOR}"

        self._print_with_decorators(self.build_id, symbol, self.message, end="")

    # pylint: disable=too-many-arguments
    def _print_with_decorators(
        self,
        sender: str,
        status_symbol: str,
        message: str,
        highlight_attr: TermAttrs = TermAttrs.FG_DEFAULT_COLOR,
        end: str = "\n",
    ) -> None:
        r"""Print line in specific format.

        Print in the format:
        `[<sender>][<status_symbol(use highlight_attr for this symbol)>] <message>`
        with ending.
        """
        print(
            f"{TermAttrs.ERASE_LINE}"
            f"{highlight_attr}"
            f"[{sender}]"
            f"[{status_symbol}]"
            f" {message}"
            f"{TermAttrs.FG_DEFAULT_COLOR}",
            end=end,
        )

    def _send_with_decorators(
        self,
        sender: str,
        status_symbol: str,
        message: str,
        highlight_attr: TermAttrs = TermAttrs.FG_DEFAULT_COLOR,
    ) -> None:
        r"""Send text message to user with highlighting.

        Print in the format:
        `[<sender>][<status_symbol>] <message(in text block, with a indent on the new line)>`
        with coloring entire message to `highlight_attr` and a new line at the end.
        """
        word_len = len(sender) + INVITATION_TEMPLATE_LEN
        to_insert = f"\n{" " * word_len}"
        bold_off = TermAttrs.FG_DEFAULT_COLOR + highlight_attr
        message = message.replace("\n", to_insert)
        self._print_with_decorators(
            sender=sender,
            status_symbol=TermAttrs.BOLD_FONT + status_symbol + bold_off,
            message=highlight_attr + message,
            highlight_attr=highlight_attr,
        )
