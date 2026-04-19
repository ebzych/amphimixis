"""CLI commands package."""

from amphimixis.cli.commands import (
    add,
    analyze,
    build,
    clean,
    compare,
    profile,
    run,
    validate,
)

COMMANDS = {
    "run": run,
    "analyze": analyze,
    "build": build,
    "profile": profile,
    "validate": validate,
    "compare": compare,
    "clean": clean,
    "add": add,
}
