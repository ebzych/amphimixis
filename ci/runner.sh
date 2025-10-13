#!/bin/bash

RED='\e[31m'
BLUE='\e[34m'
NC='\e[0m'

echo "Running shellcheck..."
shellcheck ci/*.sh

CONFIG_FILE="ci/.temp_config"
./ci/environment_configure.sh "$CONFIG_FILE"

if [ -f "$CONFIG_FILE" ]; then
    COMMAND=$(cat "$CONFIG_FILE")
    rm -f "$CONFIG_FILE"
else
    echo -e "${RED}Error: Config file not found ${NC}"
    exit 1
fi

if [ -n "$COMMAND" ]; then
    echo -e "${BLUE}Run CI:${NC}"
    ./ci/pylint.sh "$COMMAND"
    ./ci/mypy.sh "$COMMAND"
    ./ci/black.sh "$COMMAND"
else
    echo -e "${RED}Error: CI can not run ${NC}"
    exit 1
fi
