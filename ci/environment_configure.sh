#!/bin/bash

PREFIX=""
TOOL=""

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if command_exists "uv"; then
    TOOL="uv"
else
    echo "Please install uv for check CI:"
    echo "pip install uv"
    exit 1
fi

PREFIX="$HOME/.local/bin"
TOOL="uv"

if [ -n "$PREFIX" ]; then
    COMMAND="$PREFIX/$TOOL"
else
    COMMAND="$TOOL"
fi

$COMMAND sync

echo "$COMMAND"
