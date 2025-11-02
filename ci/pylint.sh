#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'
COMMAND="${1}"

echo -e "${BLUE}Running linter Pylint...${NC}"
mapfile -t files < <(git ls-files '*.py')
"$COMMAND" run pylint "${files[@]}"
