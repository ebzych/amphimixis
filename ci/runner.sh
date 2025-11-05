#!/bin/bash
set -e

BLUE='\e[34m'
NC='\e[0m'

echo "Running shellcheck..."
shellcheck ci/*.sh

./ci/environment_configure.sh

echo -e "${BLUE}Run CI:${NC}"
./ci/black.sh
./ci/mypy.sh
./ci/pylint.sh
./ci/ruff.sh
