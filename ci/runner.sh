#!/bin/bash
set -e

BLUE='\e[34m'
NC='\e[0m'

echo "Running shellcheck..."
shellcheck ci/*.sh

./ci/environment_configure.sh

CI_PATH=$(dirname "$0")

echo -e "${BLUE}Run CI:${NC}"
"${CI_PATH}"/black.sh
"${CI_PATH}"/mypy.sh
"${CI_PATH}"/pylint.sh
"${CI_PATH}"/ruff.sh
