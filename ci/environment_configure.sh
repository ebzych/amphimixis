#!/bin/bash

PREFIX=""
TOOL=""

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if command_exists "uv"; then
    TOOL="uv"
elif command_exists "poetry"; then
    TOOL="poetry"
else
    if command_exists "curl"; then
        echo -e "${BLUE}Installing uv with curl:${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif  command_exists "wget"; then
        echo -e "${BLUE}Installing uv with wget:${NC}"
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
         echo "Please install curl for check CI:"
         echo "sudo apt install curl"
         exit 1
    fi

    PREFIX="$HOME/.local/bin"
    TOOL="uv"
fi

if [ -n "$PREFIX" ]; then
    COMMAND="$PREFIX/$TOOL"
else
    COMMAND="$TOOL"
fi

$COMMAND sync

echo "$COMMAND"
