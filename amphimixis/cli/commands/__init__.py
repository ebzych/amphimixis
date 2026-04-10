"""CLI commands package."""

from amphimixis.cli.commands import add, analyze, build
from amphimixis.cli.commands import clean as clean_module
from amphimixis.cli.commands import compare, profile, run, validate

COMMANDS = {
    "run": run,
    "analyze": analyze,
    "build": build,
    "profile": profile,
    "validate": validate,
    "compare": compare,
    "clean": clean_module,
    "add": add,
}
