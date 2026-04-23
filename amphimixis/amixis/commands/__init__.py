"""CLI commands package."""

from amphimixis.amixis.commands import (
    init,
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
    "init": init,
    "run": run,
    "analyze": analyze,
    "build": build,
    "profile": profile,
    "validate": validate,
    "compare": compare,
    "clean": clean,
    "add": add,
}
