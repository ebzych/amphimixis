#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'
COMMAND="${1}"

echo -e "${BLUE}Running linter Ruff...${NC}"
mapfile -t files < <(git ls-files '*.py')
"$COMMAND" run ruff check "${files[@]}"
