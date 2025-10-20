#!/bin/bash
set -e

RED='\e[31m'
BLUE='\e[34m'
NC='\e[0m'

echo "Running shellcheck..."
shellcheck ci/*.sh

COMMAND=$(./ci/environment_configure.sh)

if [ -n "$COMMAND" ]; then
    echo -e "${BLUE}Run CI:${NC}"
    ./ci/pylint.sh "$COMMAND"
    ./ci/mypy.sh "$COMMAND"
    ./ci/black.sh "$COMMAND"
    ./ci/ruff.sh "$COMMAND"
else
    echo -e "${RED}Error: CI can not run ${NC}"
    exit 1
fi
